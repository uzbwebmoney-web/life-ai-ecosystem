from __future__ import annotations

from datetime import datetime


def next_occurrence(starts_at: datetime, now: datetime, recurrence: str | None) -> datetime:
    if recurrence == "yearly":
        try:
            candidate = starts_at.replace(year=now.year)
        except ValueError:
            candidate = starts_at.replace(year=now.year, day=28)
        if candidate < now:
            try:
                candidate = starts_at.replace(year=now.year + 1)
            except ValueError:
                candidate = starts_at.replace(year=now.year + 1, day=28)
        return candidate
    return starts_at
