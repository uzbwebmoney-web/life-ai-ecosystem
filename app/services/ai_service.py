from __future__ import annotations



import logging



from app.core.config import settings

from app.core.credits import apply_chunk_estimate, estimate_request_credits

from app.core.i18n import ai_reply_language, normalize_lang, t

from app.services.model_router import classify_query_complexity, select_ai_model

from app.services.subscription_service import (
    check_ai_quota,
    check_model_quota,
    consume_ai_request,
    max_output_tokens_for_user,
)

from app.services.text_format import format_ai_reply



logger = logging.getLogger(__name__)





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

    max_completion_tokens: int = 1200,

    module_id: str | None = None,

    submodule_id: str | None = None,
    chat_history: list[tuple[str, str]] | None = None,
    usage_source: str = "chat",
    admin_preview: str | None = None,

) -> str:

    estimate = None

    model = settings.openai_model

    if user is not None and session is not None:
        from app.services.subscription_service import QUOTA_BLOCK_PREFIX, feature_allowed

        mod_id = module_id or getattr(user, "active_module_id", None)
        sub_id = submodule_id or getattr(user, "active_submodule_id", None)
        lower = user_message.lower()
        doc_translate = sub_id == "documents" or any(
            k in lower for k in ("перевед", "translate", "tarjima", "translation")
        )
        if doc_translate:
            blocked = feature_allowed(user, "doc_translate")
            if blocked:
                return QUOTA_BLOCK_PREFIX + t(language, blocked)

    if user is not None and session is not None:

        mod_id = module_id or getattr(user, "active_module_id", None)

        sub_id = submodule_id or getattr(user, "active_submodule_id", None)

        model = select_ai_model(

            user,

            user_message,

            module_hint=module_hint,

            module_id=mod_id,

        )

        complexity = classify_query_complexity(

            user_message,

            module_hint=module_hint,

            module_id=mod_id,

        )

        raw_estimate = estimate_request_credits(

            user_message=user_message,

            model=model,

            max_output_tokens=max_completion_tokens,

            module_id=mod_id,

            submodule_id=sub_id,

            complexity=complexity,

        )

        chunk_size = max_output_tokens_for_user(user)

        estimate = apply_chunk_estimate(raw_estimate, chunk_size=chunk_size)

        model_quota = check_model_quota(user, model, lang=language)

        if model_quota:

            return model_quota

        quota_msg = await check_ai_quota(session, user, lang=language, estimate=estimate)

        if quota_msg:

            return quota_msg



    if not settings.openai_api_key.strip():

        return (

            "⚠️ OPENAI_API_KEY не задан в .env\n\n"

            f"Ваш запрос: {user_message[:500]}\n\n"

            f"Контекст модуля: {module_hint or 'общий AI-чат'}"

        )



    from openai import AsyncOpenAI



    timeout = 300.0 if max_completion_tokens > 4000 else 120.0

    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=timeout)

    reply_lang = ai_reply_language(language)

    audience = (settings.default_passport_country or "Узбекистан").strip()

    system = (

        "Ты — персональный AI-помощник экосистемы Life AI. "

        "Помогаешь человеку в повседневной жизни. "

        f"Отвечай на {reply_lang} языке, структурированно и практично. "

        "Не используй markdown (**жирный**, *курсив*, ```код```) — только обычный текст и списки. "

        "Если задан контекст модуля — строго придерживайся его темы. "

        "Используй известные факты о пользователе — не спрашивай то, что уже известно. "

        f"Аудитория сервиса — жители {audience}. Если пользователь не указал иное, для виз, "

        f"документов и правил ориентируйся на гражданство {audience} и местные реалии (сум, Uzcard). "

        "В продолжении диалога сохраняй тему и сущности из предыдущих реплик (страна поездки, даты и т.д.). "

        f"{module_hint}"

    )

    if profile_context:

        system += f"\n\n{profile_context}"

    if memory_context:

        system += f"\n\nКонтекст из памяти пользователя:\n{memory_context}"



    from app.services.openai_compat import chat_token_limit_kwargs



    parts = estimate.parts if estimate else 1

    chunk_tokens = estimate.chunk_tokens if estimate else max_completion_tokens

    answers: list[str] = []



    history = list(chat_history or [])

    def _chat_messages(user_content: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        for past_q, past_a in history:
            messages.append({"role": "user", "content": past_q})
            messages.append({"role": "assistant", "content": past_a})
        messages.append({"role": "user", "content": user_content})
        return messages

    try:

        for part_idx in range(parts):

            part_note = ""

            if parts > 1:

                part_note = (

                    f"\n\nЭто часть {part_idx + 1} из {parts}. "

                    "Продолжай материал без повторения уже написанного. "

                    "В начале ответа укажи «Часть {n}/{total}»."

                ).format(n=part_idx + 1, total=parts)

            user_content = user_message + part_note

            if part_idx > 0 and answers:

                user_content += (

                    "\n\nУже написано ранее (не повторяй):\n"

                    + answers[-1][-1500:]

                )

            logger.info(

                "AI request model=%s part=%s/%s max_tokens=%s preview=%r",

                model,

                part_idx + 1,

                parts,

                chunk_tokens,

                user_message[:120],

            )

            response = await client.chat.completions.create(

                model=model,

                messages=_chat_messages(user_content),

                **chat_token_limit_kwargs(model, chunk_tokens),

            )

            raw = (response.choices[0].message.content or "").strip()

            if not raw:

                return t(language, "ai_request_failed")

            answers.append(format_ai_reply(raw))



            if user is not None and session is not None:

                from app.services.ai_usage_service import record_ai_usage



                await record_ai_usage(session, user.id, model, response, source=usage_source)

                if bot is not None:

                    from app.services.admin_notify_service import notify_admins_ai_request

                    from app.services.ai_usage_service import extract_usage



                    prompt_tokens, completion_tokens = extract_usage(response)

                    await notify_admins_ai_request(

                        bot,

                        user,

                        model=model,

                        source=usage_source,

                        prompt_tokens=prompt_tokens,

                        completion_tokens=completion_tokens,

                        preview=admin_preview if admin_preview is not None else user_message,

                    )

    except Exception as exc:

        logger.exception("OpenAI chat failed: %s", exc)

        return t(language, "ai_request_failed")



    if user is not None and session is not None and estimate is not None:

        await consume_ai_request(session, user, credits=estimate.credits, model=model)



    return "\n\n".join(answers)


