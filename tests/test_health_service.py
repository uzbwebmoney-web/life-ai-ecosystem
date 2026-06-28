from datetime import datetime

from app.services.health_service import (
    _notify_key,
    _snooze_notify_key,
    parse_pressure,
    parse_reminder_times,
    parse_single_value,
    parse_snooze_minutes,
    user_local_now,
)


def test_parse_pressure():
    assert parse_pressure("120/80") == (120.0, 80.0)
    assert parse_pressure("invalid") is None


def test_parse_reminder_times():
    assert parse_reminder_times("08:00, 20:00") == ["08:00", "20:00"]
    assert parse_reminder_times("bad") == []


def test_parse_single_value():
    assert parse_single_value("5,6") == 5.6
    assert parse_single_value("abc") is None


def test_notify_key():
    dt = datetime(2026, 6, 23, 8, 0)
    assert _notify_key(1, dt, "08:00") == "1:2026-06-23:08:00"


def test_user_local_now_offset():
    from app.models.entities import User

    user = User(telegram_id=1, utc_offset_minutes=300)
    utc = datetime(2026, 1, 1, 10, 0)
    local = user_local_now(user, utc)
    assert local.hour == 15


def test_parse_snooze_minutes():
    assert parse_snooze_minutes("30") == 30
    assert parse_snooze_minutes("1ч") == 60
    assert parse_snooze_minutes("1:30") == 90
    assert parse_snooze_minutes("abc") is None


def test_snooze_notify_key():
    dt = datetime(2026, 6, 23, 8, 30)
    assert _snooze_notify_key(5, dt) == "snooze:5:202606230830"
