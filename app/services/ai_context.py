from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.life_data import search_memory
from app.services.life_profile_service import build_profile_context


async def build_ai_memory_context(
    session: AsyncSession,
    user: User,
    query: str,
    *,
    limit: int = 5,
) -> tuple[str, str]:
    profile_ctx = await build_profile_context(session, user.id, user.language)
    memory_ctx = ""
    if user.memory_enabled and query.strip():
        entries = await search_memory(session, user.id, query, limit=limit)
        if entries:
            memory_ctx = "\n".join(e.content for e in entries)
    return profile_ctx, memory_ctx
