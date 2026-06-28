from app.services.health_service import parse_reminder_times


def test_update_medication_times_validation():
    assert parse_reminder_times("09:00, 21:00") == ["09:00", "21:00"]
    assert parse_reminder_times("invalid") == []
