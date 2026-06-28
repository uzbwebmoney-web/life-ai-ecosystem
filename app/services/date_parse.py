from __future__ import annotations

from datetime import datetime

DATE_FMT = "%d.%m.%Y"
DATETIME_FMT = "%d.%m.%Y %H:%M"

_DATE_ONLY_FORMATS = (
    "%d.%m.%Y",
    "%Y-%m-%d",
    "%Y.%m.%d",
)

_DATETIME_FORMATS = (
    "%d.%m.%Y %H:%M",
    "%Y-%m-%d %H:%M",
    "%Y.%m.%d %H:%M",
)


def format_date(dt: datetime) -> str:
    return dt.strftime(DATE_FMT)


def format_datetime(dt: datetime) -> str:
    return dt.strftime(DATETIME_FMT)


def parse_date_flexible(raw: str) -> datetime | None:
    text = raw.strip()
    for fmt in _DATE_ONLY_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(hour=9, minute=0, second=0, microsecond=0)
        except ValueError:
            continue
    return None


def parse_datetime_flexible(raw: str) -> datetime | None:
    text = raw.strip()
    for fmt in _DATETIME_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(second=0, microsecond=0)
        except ValueError:
            continue
    return parse_date_flexible(text)
