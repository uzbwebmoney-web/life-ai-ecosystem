from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.web_search_service import append_links_footer, collect_links_from_text, fetch_web_context, merge_unique_links


async def build_research_report(
    session: AsyncSession,
    user: User,
    topic: str,
    *,
    bot=None,
    lang: str = "ru",
    depth: str = "standard",
) -> str:
    max_results = 15 if depth == "deep" else 10
    ctx, links = await fetch_web_context(topic, language=lang, max_results=max_results)
    prompt = (
        f"Подготовь структурированный отчёт на тему: {topic}\n\n"
        "Структура:\n1. Краткое резюме\n2. Ключевые факты\n3. Практические рекомендации\n4. Риски и ограничения\n5. Источники (URL)\n\n"
        f"Контекст из интернета:\n{ctx[:6000]}"
    )
    report = await ask_ai(
        user_message=prompt,
        module_hint="Research mode — deep analysis with citations.",
        language=lang,
        session=session,
        user=user,
        bot=bot,
        max_completion_tokens=4000 if depth == "deep" else 2500,
        usage_source="agent_research",
    )
    all_links = merge_unique_links(links, collect_links_from_text(report), collect_links_from_text(ctx))
    return append_links_footer(report, all_links, language=lang)
