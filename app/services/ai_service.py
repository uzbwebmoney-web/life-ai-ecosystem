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
    session=None,
    user=None,
    bot=None,
) -> str:
    if user is not None and session is not None:
        from app.services.model_router import select_ai_model
        from app.services.subscription_service import check_ai_quota, consume_ai_request

        model = select_ai_model(
            user,
            user_message,
            module_hint=module_hint,
            module_id=getattr(user, "active_module_id", None),
        )
        quota_msg = await check_ai_quota(session, user, lang=language, model=model)
        if quota_msg:
            return quota_msg
    else:
        model = settings.openai_model

    if not settings.openai_api_key.strip():
        return (
            "⚠️ OPENAI_API_KEY не задан в .env\n\n"
            f"Ваш запрос: {user_message[:500]}\n\n"
            f"Контекст модуля: {module_hint or 'общий AI-чат'}"
        )

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    reply_lang = ai_reply_language(language)
    if user is None:
        model = settings.openai_model
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
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        **chat_token_limit_kwargs(model, 1200),
    )
    raw = (response.choices[0].message.content or "").strip()
    if user is not None and session is not None:
        from app.services.subscription_service import consume_ai_request
        from app.services.ai_usage_service import record_ai_usage

        await consume_ai_request(session, user, model=model)
        await record_ai_usage(session, user.id, model, response, source="chat")
        if bot is not None:
            from app.services.admin_notify_service import notify_admins_ai_request
            from app.services.ai_usage_service import extract_usage

            prompt_tokens, completion_tokens = extract_usage(response)
            await notify_admins_ai_request(
                bot,
                user,
                model=model,
                source="chat",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                preview=user_message,
            )
    return format_ai_reply(raw)
