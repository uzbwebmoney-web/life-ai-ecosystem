from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.life_profile_service import extract_facts_from_text, upsert_fact

_UNIFIED_FACT_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (r"(?:мой автомобиль|моя машина|у меня)\s+([A-Za-zА-Яа-яЁё0-9\s\-]+)", "car", "car_model"),
    (r"(?:my car|i drive)\s+([A-Za-z0-9\s\-]+)", "car", "car_model"),
    (r"([A-Za-z]+\s+[A-Z]\d+)", "car", "car_model"),
    (r"аллерг(?:ия|ии)\s*(?:на|to)?\s*(.+)", "health", "allergy"),
    (r"allerg(?:y|ic)\s*(?:to)?\s*(.+)", "health", "allergy"),
    (r"(?:живу в|i live in|yashayman)\s+(.+)", "profile", "city"),
    (r"(?:мой вес|вешу)\s*(\d+\s*кг)", "health", "weight"),
)


async def ingest_unified_facts(session: AsyncSession, user_id: int, text: str) -> list[str]:
    saved = await extract_facts_from_text(session, user_id, text)
    for pattern, category, key in _UNIFIED_FACT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        value = match.group(1).strip().rstrip(".")[:500]
        if len(value) >= 2:
            await upsert_fact(session, user_id, category=category, fact_key=key, fact_value=value)
            token = f"{key}={value}"
            if token not in saved:
                saved.append(token)
    return saved
