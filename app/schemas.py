from datetime import datetime
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    feedback_id: str
    booking_id: str
    sitter_id: str
    rating: int
    comment: str | None = None
    is_moderated: bool = False


class FeedbackOut(FeedbackCreate):
    moderated_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class RatingAggregateOut(BaseModel):
    sitter_id: str
    average_rating: float
    reviews_count: int
    updated_at: datetime

    class Config:
        from_attributes = True
