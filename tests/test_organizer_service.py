from datetime import datetime

from app.models.entities import CalendarEvent, OrganizerItem, Reminder
from app.services.organizer_service import (
    EVENT_TYPES,
    ORGANIZER_MODULE,
    format_event_line,
    format_note_line,
    format_reminder_line,
    format_task_line,
    parse_datetime,
)


def test_parse_datetime_full():
    dt = parse_datetime("2026-06-25 18:00")
    assert dt == datetime(2026, 6, 25, 18, 0)


def test_parse_datetime_date_only():
    dt = parse_datetime("25.06.2026")
    assert dt == datetime(2026, 6, 25, 9, 0)


def test_parse_datetime_invalid():
    assert parse_datetime("not-a-date") is None


def test_format_task_line_open():
    item = OrganizerItem(title="Buy milk", done=False)
    assert "⬜" in format_task_line(item)
    assert "Buy milk" in format_task_line(item)


def test_format_task_line_done():
    item = OrganizerItem(title="Done task", done=True, due_at=datetime(2026, 6, 25, 10, 0))
    line = format_task_line(item)
    assert "✅" in line
    assert "25.06.2026" in line


def test_format_note_line():
    item = OrganizerItem(title="Idea", body="Call client tomorrow")
    line = format_note_line(item)
    assert "Idea" in line
    assert "Call client" in line


def test_format_event_line():
    event = CalendarEvent(title="Sync", starts_at=datetime(2026, 7, 1, 15, 0), event_type="meeting")
    line = format_event_line(event)
    assert "🤝" in line
    assert "Sync" in line


def test_format_reminder_line():
    reminder = Reminder(title="Pay bill", due_at=datetime(2026, 6, 30, 9, 0))
    line = format_reminder_line(reminder)
    assert "🔔" in line
    assert "Pay bill" in line


def test_constants():
    assert ORGANIZER_MODULE == "organizer"
    assert "meeting" in EVENT_TYPES
    assert "birthday" in EVENT_TYPES
