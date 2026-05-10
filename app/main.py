from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .init_db import create_schema_and_tables, seed_stub_data
from .logging_config import configure_logging, get_logger
from .models import Feedback, SitterRatingAggregate
from .schemas import FeedbackCreate, FeedbackOut, RatingAggregateOut
from .service_bus_consumer import start_consumer_in_background

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Feedback Service")


@app.on_event("startup")
def startup() -> None:
    logger.info("Feedback service is starting up")
    create_schema_and_tables()
    start_consumer_in_background()
    logger.info("Feedback service startup completed")


@app.get("/health")
def health():
    logger.debug("Health check requested")
    return {"service": "feedback_service", "status": "ok"}


@app.post("/init-db")
def init_db():
    logger.info("Manual /init-db invoked")
    create_schema_and_tables()
    return {"status": "ok", "schema": "feedback"}


@app.post("/seed")
def seed():
    logger.info("Manual /seed invoked")
    seed_stub_data()
    return {"status": "ok", "schema": "feedback", "message": "stub data inserted"}


@app.get("/feedback", response_model=list[FeedbackOut])
def get_feedback_list(db: Session = Depends(get_db)):
    logger.info("GET /feedback")
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()


@app.get("/feedback/{feedback_id}", response_model=FeedbackOut)
def get_feedback(feedback_id: str, db: Session = Depends(get_db)):
    logger.info("GET /feedback/%s", feedback_id)
    item = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if not item:
        logger.warning("Feedback not found: %s", feedback_id)
        raise HTTPException(status_code=404, detail="Feedback not found")
    return item


@app.post("/feedback", response_model=FeedbackOut)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    logger.info("POST /feedback feedback_id=%s booking_id=%s", payload.feedback_id, payload.booking_id)
    try:
        item = Feedback(
            feedback_id=payload.feedback_id,
            booking_id=payload.booking_id,
            sitter_id=payload.sitter_id,
            rating=payload.rating,
            comment=payload.comment,
            is_moderated=payload.is_moderated,
            moderated_at=None,
            created_at=datetime.utcnow(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info("Feedback created: %s", item.feedback_id)
        return item
    except Exception as ex:
        logger.exception("Failed to create feedback: %s", ex)
        raise HTTPException(status_code=500, detail=str(ex))


@app.get("/rating-aggregates", response_model=list[RatingAggregateOut])
def get_rating_aggregates(db: Session = Depends(get_db)):
    logger.info("GET /rating-aggregates")
    return db.query(SitterRatingAggregate).order_by(SitterRatingAggregate.average_rating.desc()).all()
