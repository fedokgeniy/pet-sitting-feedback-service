from sqlalchemy import Column, Text, DateTime, Numeric, Integer, Boolean, String, ForeignKey

from .database import Base


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {"schema": "feedback"}

    feedback_id = Column(String(36), primary_key=True)
    booking_id = Column(String(36), nullable=False, unique=True)
    sitter_id = Column(String(36), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    is_moderated = Column(Boolean, nullable=False)
    moderated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)


class FeedbackReport(Base):
    __tablename__ = "feedback_reports"
    __table_args__ = {"schema": "feedback"}

    report_id = Column(String(36), primary_key=True)
    feedback_id = Column(String(36), ForeignKey("feedback.feedback.feedback_id"), nullable=False)
    reporter_user_id = Column(String(36), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime, nullable=False)


class SitterRatingAggregate(Base):
    __tablename__ = "sitter_rating_aggregates"
    __table_args__ = {"schema": "feedback"}

    sitter_id = Column(String(36), primary_key=True)
    average_rating = Column(Numeric(3, 2), nullable=False)
    reviews_count = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False)
