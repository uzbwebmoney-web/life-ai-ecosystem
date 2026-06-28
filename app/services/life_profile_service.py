from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import LifeProfileFact

REMEMBER_PREFIXES: tuple[tuple[str, str], ...] = (
    ("запомни:", "ru"),
    ("запомни ", "ru"),
    ("remember:", "en"),
    ("remember ", "en"),
    ("eslab qol:", "uz"),
    ("eslab qol ", "uz"),
)

FACT_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (r"(?:моя машина|у меня|авто)\s*[—:-]?\s*(.+)", "car", "car_model"),
    (r"(?:my car|i have a)\s*(.+)", "car", "car_model"),
    (r"аллерг(?:ия|ии)\s*(?:на|to)?\s*(.+)", "health", "allergy"),
    (r"allerg(?:y|ic)\s*(?:to)?\s*(.+)", "health", "allergy"),
)


def parse_remember_text(text: str) -> str | None:
    lowered = text.strip().lower()
    for prefix, _ in REMEMBER_PREFIXES:
        if lowered.startswith(prefix):
            return text.strip()[len(prefix) :].strip()
    return None


async def upsert_fact(
    session: AsyncSession,
    user_id: int,
    *,
    category: str,
    fact_key: str,
    fact_value: str,
) -> LifeProfileFact:
    value = fact_value.strip()[:2000]
    row = (
        await session.execute(
            select(LifeProfileFact).where(
                LifeProfileFact.user_id == user_id,
                LifeProfileFact.fact_key == fact_key,
            )
        )
    ).scalar_one_or_none()
    if row:
        row.category = category
        row.fact_value = value
        row.updated_at = datetime.utcnow()
    else:
        row = LifeProfileFact(user_id=user_id, category=category, fact_key=fact_key, fact_value=value)
        session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def extract_facts_from_text(session: AsyncSession, user_id: int, text: str) -> list[str]:
    saved: list[str] = []
    for pattern, category, key in FACT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip().rstrip(".")
            if len(value) >= 2:
                await upsert_fact(session, user_id, category=category, fact_key=key, fact_value=value)
                saved.append(f"{key}={value}")
    return saved


async def list_profile_facts(session: AsyncSession, user_id: int) -> list[LifeProfileFact]:
    rows = (
        await session.execute(
            select(LifeProfileFact).where(LifeProfileFact.user_id == user_id).order_by(LifeProfileFact.fact_key)
        )
    ).scalars().all()
    return list(rows)


async def build_profile_context(session: AsyncSession, user_id: int, lang: str = "ru") -> str:
    facts = await list_profile_facts(session, user_id)
    if not facts:
        return ""
    lines = ["Известные факты о пользователе:" if lang == "ru" else "Known user facts:"]
    for fact in facts[:20]:
        lines.append(f"- {fact.fact_key}: {fact.fact_value}")
    return "\n".join(lines)
