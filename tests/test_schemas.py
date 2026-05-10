from app.schemas import FeedbackCreate, RatingAggregateOut


def test_feedback_create_default_moderation():
    payload = FeedbackCreate(
        feedback_id="f1",
        booking_id="b1",
        sitter_id="s1",
        rating=5,
    )
    assert payload.is_moderated is False
    assert payload.comment is None


def test_feedback_create_with_comment():
    payload = FeedbackCreate(
        feedback_id="f2",
        booking_id="b2",
        sitter_id="s2",
        rating=4,
        comment="Friendly",
        is_moderated=True,
    )
    assert payload.comment == "Friendly"
    assert payload.is_moderated is True


def test_rating_aggregate_out_types():
    from datetime import datetime
    agg = RatingAggregateOut(
        sitter_id="s1",
        average_rating=4.5,
        reviews_count=10,
        updated_at=datetime.utcnow(),
    )
    assert agg.average_rating == 4.5
    assert agg.reviews_count == 10
