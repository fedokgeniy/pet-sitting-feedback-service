from datetime import datetime

from sqlalchemy.orm import Session

from .database import Base, engine, ensure_schema
from .logging_config import get_logger
from .models import Feedback, FeedbackReport, SitterRatingAggregate

logger = get_logger(__name__)


def create_schema_and_tables() -> None:
    logger.info("Creating schema 'feedback' and its tables")
    ensure_schema("feedback")
    Base.metadata.create_all(
        bind=engine,
        tables=[
            Feedback.__table__,
            FeedbackReport.__table__,
            SitterRatingAggregate.__table__,
        ],
    )
    logger.info("Schema 'feedback' is ready")


def seed_stub_data() -> None:
    logger.info("Seeding stub data for feedback service")
    with Session(engine) as session:
        if session.query(Feedback).first():
            logger.info("Stub data already present, skip seeding")
            return

        feedback1 = Feedback(
            feedback_id="cccccccc-cccc-cccc-cccc-ccccccccccc1",
            booking_id="88888888-8888-8888-8888-888888888881",
            sitter_id="11111111-1111-1111-1111-111111111111",
            rating=5,
            comment="Great service and communication",
            is_moderated=True,
            moderated_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        feedback2 = Feedback(
            feedback_id="cccccccc-cccc-cccc-cccc-ccccccccccc2",
            booking_id="88888888-8888-8888-8888-888888888882",
            sitter_id="22222222-2222-2222-2222-222222222222",
            rating=4,
            comment="Very friendly sitter",
            is_moderated=False,
            moderated_at=None,
            created_at=datetime.utcnow(),
        )

        session.add_all([feedback1, feedback2])
        session.flush()

        session.add_all([
            FeedbackReport(
                report_id="dddddddd-dddd-dddd-dddd-ddddddddddd1",
                feedback_id=feedback2.feedback_id,
                reporter_user_id="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1",
                reason="Contains misleading statement",
                status="open",
                created_at=datetime.utcnow(),
            ),
            SitterRatingAggregate(
                sitter_id="11111111-1111-1111-1111-111111111111",
                average_rating=5.00,
                reviews_count=1,
                updated_at=datetime.utcnow(),
            ),
            SitterRatingAggregate(
                sitter_id="22222222-2222-2222-2222-222222222222",
                average_rating=4.00,
                reviews_count=1,
                updated_at=datetime.utcnow(),
            ),
        ])

        session.commit()
        logger.info("Stub data seeded successfully")
