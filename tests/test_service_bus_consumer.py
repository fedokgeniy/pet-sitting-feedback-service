from unittest.mock import patch, MagicMock

from app import service_bus_consumer


def test_process_message_ignores_non_booking_event():
    # Should not touch the DB at all
    with patch.object(service_bus_consumer, "Session") as session_cls:
        service_bus_consumer.process_message_data({"event_type": "Other", "payload": {}})
        session_cls.assert_not_called()


def test_process_message_ignores_missing_ids():
    with patch.object(service_bus_consumer, "Session") as session_cls:
        service_bus_consumer.process_message_data(
            {"event_type": "BookingCompleted", "payload": {}}
        )
        session_cls.assert_not_called()


def test_process_message_creates_stub_when_no_existing():
    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_session
    fake_session.__exit__.return_value = False
    fake_session.query.return_value.filter.return_value.first.return_value = None

    with patch.object(service_bus_consumer, "Session", return_value=fake_session):
        service_bus_consumer.process_message_data({
            "event_type": "BookingCompleted",
            "payload": {"booking_id": "B1", "sitter_id": "S1"},
        })

    assert fake_session.add.called
    assert fake_session.commit.called
