from datetime import datetime

from app.services.recurrence import next_occurrence


def test_yearly_birthday_this_year():
    now = datetime(2026, 6, 1)
    birth = datetime(1990, 8, 15, 9, 0)
    nxt = next_occurrence(birth, now, "yearly")
    assert nxt.year == 2026
    assert nxt.month == 8


def test_yearly_birthday_next_year_if_passed():
    now = datetime(2026, 12, 1)
    birth = datetime(1990, 3, 10, 9, 0)
    nxt = next_occurrence(birth, now, "yearly")
    assert nxt.year == 2027


def test_no_recurrence_unchanged():
    now = datetime(2026, 6, 1)
    dt = datetime(2026, 7, 1)
    assert next_occurrence(dt, now, "") == dt
