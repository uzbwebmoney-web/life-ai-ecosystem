from datetime import datetime

from app.services.car_service import parse_date


def test_parse_date_iso():
    dt = parse_date("2026-07-15")
    assert dt is not None
    assert dt.day == 15 and dt.month == 7


def test_parse_date_eu():
    dt = parse_date("15.07.2026")
    assert dt is not None
    assert dt.year == 2026


def test_parse_date_invalid():
    assert parse_date("bad") is None
