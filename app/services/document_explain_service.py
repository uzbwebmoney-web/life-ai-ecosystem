from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.ai_service import ask_ai


async def explain_document_text(
    session: AsyncSession,
    user: User,
    text: str,
    *,
    risk_check: bool = True,
    bot=None,
    lang: str = "ru",
) -> str:
    prompt = (
        "Объясни документ простыми словами для обычного человека.\n"
        "Структура:\n"
        "1. О чём документ (1-2 предложения)\n"
        "2. Ключевые обязательства сторон\n"
        "3. Сроки и суммы\n"
        "4. На что обратить внимание\n"
    )
    if risk_check:
        prompt += "5. Риски при подписании (🟢 низкий / 🟡 средний / 🔴 высокий) с кратким обоснованием\n"
    prompt += f"\n\nТекст документа:\n{text[:12000]}"
    return await ask_ai(
        user_message=prompt,
        module_hint="Legal document explainer — plain language, no legal advice disclaimer at end.",
        language=lang,
        session=session,
        user=user,
        bot=bot,
        max_completion_tokens=2500,
        module_id="legal",
        submodule_id="doc_check",
        usage_source="agent_doc_explain",
    )
