import json
import os
import time
from datetime import datetime
from threading import Thread

from azure.servicebus import ServiceBusClient
from sqlalchemy.orm import Session

from .database import engine
from .logging_config import get_logger
from .models import Feedback, SitterRatingAggregate

logger = get_logger(__name__)

QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME")
RECEIVE_CONNECTION_STRING = os.getenv("SERVICE_BUS_RECEIVE_CONNECTION_STRING")
POLL_INTERVAL_SECONDS = int(os.getenv("SERVICE_BUS_POLL_INTERVAL_SECONDS", "10"))

_worker_started = False


def process_message_data(data: dict) -> None:
    event_type = data.get("event_type")
    payload = data.get("payload", {})
    logger.debug("Processing message event_type=%s payload=%s", event_type, payload)

    if event_type != "BookingCompleted":
        logger.debug("Skip non-BookingCompleted event: %s", event_type)
        return

    booking_id = payload.get("booking_id")
    sitter_id = payload.get("sitter_id")
    if not booking_id or not sitter_id:
        logger.warning("Message missing booking_id or sitter_id: %s", payload)
        return

    with Session(engine) as session:
        existing = session.query(Feedback).filter(Feedback.booking_id == booking_id).first()
        if existing:
            logger.info("Feedback for booking %s already exists, skip", booking_id)
            return

        feedback_stub = Feedback(
            feedback_id=f"auto-{booking_id}",
            booking_id=booking_id,
            sitter_id=sitter_id,
            rating=0,
            comment="AUTO_PLACEHOLDER_WAITING_FOR_REAL_FEEDBACK",
            is_moderated=False,
            moderated_at=None,
            created_at=datetime.utcnow(),
        )
        session.add(feedback_stub)

        aggregate = session.query(SitterRatingAggregate).filter(
            SitterRatingAggregate.sitter_id == sitter_id
        ).first()
        if not aggregate:
            aggregate = SitterRatingAggregate(
                sitter_id=sitter_id,
                average_rating=0,
                reviews_count=0,
                updated_at=datetime.utcnow(),
            )
            session.add(aggregate)
        else:
            aggregate.updated_at = datetime.utcnow()

        session.commit()
        logger.info("Feedback stub created for booking_id=%s sitter_id=%s", booking_id, sitter_id)


def consumer_loop() -> None:
    if not RECEIVE_CONNECTION_STRING or not QUEUE_NAME:
        logger.warning("Service Bus receive config missing, consumer not started")
        return

    logger.info("Service Bus consumer loop started, queue=%s", QUEUE_NAME)
    while True:
        try:
            with ServiceBusClient.from_connection_string(RECEIVE_CONNECTION_STRING) as client:
                with client.get_queue_receiver(queue_name=QUEUE_NAME) as receiver:
                    messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                    if messages:
                        logger.info("Received %d messages from Service Bus", len(messages))
                    for msg in messages:
                        try:
                            raw = b"".join([bytes(part) for part in msg.body]).decode("utf-8")
                            data = json.loads(raw)
                            process_message_data(data)
                            receiver.complete_message(msg)
                        except Exception as ex:
                            logger.exception("Message processing failed: %s", ex)
        except Exception as ex:
            logger.exception("Service Bus consumer error: %s", ex)

        time.sleep(POLL_INTERVAL_SECONDS)


def start_consumer_in_background() -> None:
    global _worker_started
    if _worker_started:
        logger.debug("Consumer already started, skip")
        return

    _worker_started = True
    thread = Thread(target=consumer_loop, daemon=True)
    thread.start()
    logger.info("Service Bus consumer thread started")
