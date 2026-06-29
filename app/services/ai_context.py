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
    if query.strip():
        from app.services.workspace_rag_service import build_workspace_rag_context

        ws = await build_workspace_rag_context(session, user, query, limit=3)
        if ws:
            memory_ctx = f"{memory_ctx}\n\n{ws}".strip() if memory_ctx else ws
    return profile_ctx, memory_ctx
