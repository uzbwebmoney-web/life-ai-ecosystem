from datetime import datetime

from app.services.credit_loans import payment_day_matches_today


def test_payment_day_matches_exact():
    assert payment_day_matches_today(15, datetime(2026, 6, 15, 10, 0))


def test_payment_day_no_match():
    assert not payment_day_matches_today(15, datetime(2026, 6, 14, 10, 0))


def test_payment_day_31_in_february():
    assert payment_day_matches_today(31, datetime(2026, 2, 28, 9, 0))
    assert not payment_day_matches_today(31, datetime(2026, 2, 27, 9, 0))
