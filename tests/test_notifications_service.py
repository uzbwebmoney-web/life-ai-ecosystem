from datetime import datetime

from app.models.entities import AlertItem
from app.services.notifications_service import (
    _effective_remind_at,
    alert_type_def,
    build_alert_reminder_text,
    format_alert_line,
)


def test_alert_type_defs():
    movie = alert_type_def("movie")
    assert movie.icon == "🎬"
    assert not movie.date_only
    assert movie.default_before_min == 30
    sub = alert_type_def("subscription")
    assert sub.needs_amount


def test_effective_remind_at_movie():
    item = AlertItem(
        alert_type="movie",
        title="Dune 3",
        due_at=datetime(2026, 6, 25, 20, 0),
        remind_before_minutes=30,
    )
    remind = _effective_remind_at(item)
    assert remind == datetime(2026, 6, 25, 19, 30)


def test_format_alert_line_event_shows_time():
    item = AlertItem(
        alert_type="event",
        title="Concert",
        due_at=datetime(2026, 7, 1, 18, 0),
        notes="Arena",
    )
    line = format_alert_line(item, "ru")
    assert "18:00" in line
    assert "Concert" in line


def test_build_alert_reminder_movie_ru():
    item = AlertItem(
        alert_type="movie",
        title="Avatar",
        due_at=datetime(2026, 6, 25, 19, 30),
        notes="Cinema City",
    )
    text = build_alert_reminder_text(item, "ru")
    assert "Avatar" in text
    assert "Cinema City" in text
    assert "🎬" in text
