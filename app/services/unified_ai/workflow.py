from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ai_reply_ui import deliver_ai_reply
from app.bot.handlers.agent import handle_agent_message
from app.bot.keyboards import back_menu_kb
from app.bot.reply_menu import thinking_reply_markup
from app.bot.voice_reply import maybe_send_voice_reply
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.life_data import add_memory
from app.services.personalization_service import personalization_system_note
from app.services.study_notes_service import prepare_study_notes_request
from app.services.unified_ai.cross_context import build_unified_ai_context, unified_system_prompt
from app.services.unified_ai.intent_router import analyze_intent
from app.services.unified_ai.memory_hub import ingest_unified_facts
from app.services.unified_ai.schemas import UnifiedResult
from app.services.unified_ai.suggestions import should_offer_save, smart_suggestions, unified_reply_kb

logger = logging.getLogger(__name__)


async def process_unified_message(
    message: Message,
    *,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    text: str,
) -> UnifiedResult:
    lang = user.language
    intent = analyze_intent(text, active_module=user.active_module_id)
    await ingest_unified_facts(session, user.id, text)

    agent_mode = (user.agent_mode or "auto").lower()
    if agent_mode != "off" and (agent_mode == "always" or intent.needs_agent):
        await handle_agent_message(
            message,
            user,
            session,
            state,
            text,
            intent=intent,
        )
        return UnifiedResult(handled=True, used_agent=True)

    profile_ctx, memory_ctx, _cross = await build_unified_ai_context(session, user, text, intent.modules)
    module_id = user.active_module_id or (intent.modules[0] if intent.modules else "ai_assistant")
    submodule_id = user.active_submodule_id

    hint = unified_system_prompt(intent.modules, lang=lang)
    hint = f"{hint}\n{personalization_system_note(user)}"
    ai_message = text
    token_limit = 4000

    if module_id == "education" and submodule_id:
        from app.services.intent_router import module_hint

        study_msg, study_hint, token_limit = prepare_study_notes_request(
            module_id,
            submodule_id,
            text,
            module_hint(module_id, submodule_id, lang=lang),
        )
        ai_message = study_msg
        hint = f"{study_hint}\n{hint}"

    if module_id in MODULE_BY_ID:
        from app.services.subscription_service import check_module_access

        blocked = await check_module_access(session, user, module_id, lang=lang)
        if blocked:
            from app.bot.quota_ui import answer_quota_block

            await answer_quota_block(message, blocked, lang=lang)
            return UnifiedResult(handled=True, used_agent=False)

    loading = await message.answer(t(lang, "uni_thinking"), reply_markup=thinking_reply_markup(lang))
    try:
        answer = await ask_ai(
            user_message=ai_message,
            module_hint=hint,
            memory_context=memory_ctx,
            profile_context=profile_ctx,
            language=lang,
            session=session,
            user=user,
            bot=bot,
            max_completion_tokens=token_limit,
            module_id=module_id if module_id in MODULE_BY_ID else "ai_assistant",
            submodule_id=submodule_id,
        )
        actions = smart_suggestions(intent, text, answer, lang)
        offer_save = should_offer_save(intent, text, answer, memory_enabled=user.memory_enabled)
        kb = unified_reply_kb(actions, lang, offer_save=offer_save) or back_menu_kb(lang)

        modules_label = ", ".join(intent.modules[:4])
        prefix = t(lang, "uni_reply_prefix", modules=modules_label) + "\n\n"

        is_quota = await deliver_ai_reply(loading, answer, lang=lang, prefix=prefix, reply_markup=kb)

        if module_id == "education" and not is_quota:
            from app.bot.handlers.study_export import after_study_ai_response

            await after_study_ai_response(
                message,
                user,
                session,
                user_text=text,
                answer=answer,
                module_id=module_id,
                submodule_id=submodule_id or "notes",
            )

        await maybe_send_voice_reply(message, user, answer)

        if not is_quota:
            await state.update_data(last_unified_q=text, last_unified_a=answer[:2000])
            if user.memory_enabled and not offer_save:
                await add_memory(
                    session,
                    user.id,
                    f"Q: {text[:200]}\nA: {answer[:400]}",
                    module_id=module_id if module_id in MODULE_BY_ID else "ai_assistant",
                    profile_id=user.active_profile_id,
                )
    except Exception:
        logger.exception("Unified AI reply failed")
        await deliver_long_text_safe(loading, t(lang, "ai_request_failed"), lang, reply_markup=back_menu_kb(lang))

    return UnifiedResult(handled=True, used_agent=False)


async def deliver_long_text_safe(loading, text, lang, reply_markup=None):
    from app.bot.message_ui import deliver_long_text

    await deliver_long_text(loading, text, reply_markup=reply_markup)
