from __future__ import annotations

from app.core.config import settings


from app.core.i18n import ai_reply_language, normalize_lang
from app.services.text_format import format_ai_reply


async def ask_ai(
    *,
    user_message: str,
    module_hint: str = "",
    memory_context: str = "",
    profile_context: str = "",
    language: str = "ru",
) -> str:
    if not settings.openai_api_key.strip():
        return (
            "⚠️ OPENAI_API_KEY не задан в .env\n\n"
            f"Ваш запрос: {user_message[:500]}\n\n"
            f"Контекст модуля: {module_hint or 'общий AI-чат'}"
        )

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    reply_lang = ai_reply_language(language)
    system = (
        "Ты — персональный AI-помощник экосистемы Life AI. "
        "Помогаешь человеку в повседневной жизни. "
        f"Отвечай на {reply_lang} языке, структурированно и практично. "
        "Не используй markdown (**жирный**, *курсив*, ```код```) — только обычный текст и списки. "
        "Если задан контекст модуля — строго придерживайся его темы. "
        "Используй известные факты о пользователе — не спрашивай то, что уже известно. "
        f"{module_hint}"
    )
    if profile_context:
        system += f"\n\n{profile_context}"
    if memory_context:
        system += f"\n\nКонтекст из памяти пользователя:\n{memory_context}"

    from app.services.openai_compat import chat_token_limit_kwargs

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        **chat_token_limit_kwargs(settings.openai_model, 1200),
    )
    raw = (response.choices[0].message.content or "").strip()
    return format_ai_reply(raw)
