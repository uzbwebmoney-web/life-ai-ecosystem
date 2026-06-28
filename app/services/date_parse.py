from __future__ import annotations

from datetime import datetime


def parse_datetime_flexible(raw: str) -> datetime | None:
    text = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            if fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                return dt.replace(hour=9, minute=0, second=0, microsecond=0)
            return dt.replace(second=0, microsecond=0)
        except ValueError:
            continue
    return None
