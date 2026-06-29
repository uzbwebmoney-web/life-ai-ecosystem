from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ai_reply_ui import deliver_ai_reply
from app.bot.message_ui import deliver_long_text
from app.bot.keyboards_education import module_reply_kb, study_spec_kb
from app.bot.states import EducationStates
from app.bot.voice_reply import maybe_send_voice_reply
from app.bot.keyboards import back_menu_kb, dashboard_kb
from app.core.modules.catalog import MODULE_BY_ID
from app.core.i18n import t
from app.models.entities import User
from app.services.ai_context import build_ai_memory_context
from app.services.ai_service import ask_ai
from app.services.intent_router import detect_module, module_hint
from app.services.life_data import add_memory
from app.services.life_profile_service import extract_facts_from_text, parse_remember_text, upsert_fact
from app.services.module_context import active_module_label
from app.services.proactive_service import proactive_kb, suggest_actions
from app.services.study_notes_service import (
    needs_study_document_clarification,
    prepare_study_notes_request,
)
from app.services.ai_chat_history import (
    append_turn,
    module_history_key,
    normalize_history,
    serialize_history,
)

router = Router()
logger = logging.getLogger(__name__)


async def answer_in_module(
    message: Message,
    *,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    text: str,
    module_id: str,
    submodule_id: str | None = None,
) -> None:
    await _answer_in_module(
        message,
        user=user,
        session=session,
        state=state,
        text=text,
        module_id=module_id,
        submodule_id=submodule_id,
        bot=bot,
    )


async def _answer_in_module(
    message: Message,
    *,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    text: str,
    module_id: str,
    submodule_id: str | None = None,
    bot: Bot | None = None,
) -> None:
    lang = user.language
    mod = MODULE_BY_ID.get(module_id)
    if not mod:
        return

    data = await state.get_data()
    hist_key = module_history_key(module_id, submodule_id)
    chat_history = normalize_history(data.get(hist_key))

    hint = module_hint(module_id, submodule_id, lang=lang)
    ai_message, ai_hint, token_limit = prepare_study_notes_request(module_id, submodule_id, text, hint)
    profile_ctx, memory_ctx = await build_ai_memory_context(session, user, text)

    loading = await message.answer(
        t(lang, "ai_module_thinking", emoji=mod.emoji, module=mod.title(lang))
    )
    try:
        if token_limit > 4000:
            await loading.edit_text(
                t(lang, "edu_long_notes_wait", emoji=mod.emoji, module=mod.title(lang))
            )
        answer = await ask_ai(
            user_message=ai_message,
            module_hint=ai_hint,
            memory_context=memory_ctx,
            profile_context=profile_ctx,
            language=lang,
            session=session,
            user=user,
            bot=bot or message.bot,
            max_completion_tokens=token_limit,
            module_id=module_id,
            submodule_id=submodule_id,
            chat_history=chat_history,
        )
        header = active_module_label(module_id, submodule_id, lang=lang)
        actions = suggest_actions(text, answer, lang, module_id=module_id)
        kb = proactive_kb(actions, lang) or module_reply_kb(module_id, submodule_id, lang)
        is_quota = await deliver_ai_reply(
            loading,
            answer,
            lang=lang,
            prefix=f"{header}\n\n" if header else "",
            reply_markup=kb,
        )

        from app.bot.handlers.study_export import after_study_ai_response

        if not is_quota:
            await after_study_ai_response(
                message,
                user,
                session,
                user_text=text,
                answer=answer,
                module_id=module_id,
                submodule_id=submodule_id or ("notes" if module_id == "education" else None),
            )

        await maybe_send_voice_reply(message, user, answer)

        if not is_quota and user.memory_enabled:
            await add_memory(
                session,
                user.id,
                f"Q: {text[:200]}\nA: {answer[:400]}",
                module_id=module_id,
                profile_id=user.active_profile_id,
            )
        if not is_quota:
            await state.update_data(**{hist_key: serialize_history(append_turn(chat_history, text, answer))})
    except Exception:
        logger.exception("Module AI reply failed module=%s sub=%s", module_id, submodule_id)
        kb = module_reply_kb(module_id, submodule_id, lang) if submodule_id or module_id else back_menu_kb(lang)
        await deliver_long_text(loading, t(lang, "ai_request_failed"), reply_markup=kb)


@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def free_text_router(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (message.text or "").strip()
    if not text:
        return
    if user.active_module_id == "ai_assistant" and user.active_submodule_id == "images":
        if len(text) < 2:
            return
    elif len(text) < 3:
        return

    remember = parse_remember_text(text)
    if remember:
        await add_memory(session, user.id, remember, module_id="profile", profile_id=user.active_profile_id)
        await extract_facts_from_text(session, user.id, remember)
        await message.answer(t(lang, "remember_saved", text=remember[:200]), reply_markup=dashboard_kb(lang))
        return

    if user.active_module_id == "ai_assistant" and user.active_submodule_id == "images":
        from app.bot.handlers.assistant import reply_with_generated_image

        await reply_with_generated_image(message, user, session, text)
        return

    if user.active_module_id and user.active_module_id in MODULE_BY_ID:
        from app.services.subscription_service import check_module_access

        blocked = await check_module_access(session, user, user.active_module_id, lang=lang)
        if blocked:
            from app.bot.quota_ui import answer_quota_block

            await answer_quota_block(message, blocked, lang=lang)
            return
        if user.active_module_id == "education":
            from app.bot.handlers.study_export import try_format_only_export

            if await try_format_only_export(message, user, session, text):
                return
            if needs_study_document_clarification(
                user.active_module_id,
                user.active_submodule_id,
                text,
            ):
                await state.set_state(EducationStates.waiting_study_spec)
                await state.update_data(
                    study_topic=text,
                    study_module_id=user.active_module_id,
                    study_submodule_id=user.active_submodule_id,
                )
                await message.answer(t(lang, "edu_ask_format_pages"), reply_markup=study_spec_kb(lang))
                return
        if user.active_module_id == "car" and len(text) > 5:
            await upsert_fact(session, user.id, category="car", fact_key="car_model", fact_value=text[:200])
        await _answer_in_module(
            message,
            user=user,
            session=session,
            state=state,
            text=text,
            module_id=user.active_module_id,
            submodule_id=user.active_submodule_id,
            bot=message.bot,
        )
        return

    module_id = detect_module(text)
    if module_id and module_id in MODULE_BY_ID:
        from app.services.subscription_service import check_module_access

        blocked = await check_module_access(session, user, module_id, lang=lang)
        if blocked:
            from app.bot.quota_ui import answer_quota_block

            await answer_quota_block(message, blocked, lang=lang)
            return
        await _answer_in_module(message, user=user, session=session, state=state, text=text, module_id=module_id)
        return

    profile_ctx, memory_ctx = await build_ai_memory_context(session, user, text)
    loading = await message.answer(t(lang, "ai_thinking"))
    answer = await ask_ai(
        user_message=text,
        memory_context=memory_ctx,
        profile_context=profile_ctx,
        language=lang,
        session=session,
        user=user,
        bot=message.bot,
    )
    actions = suggest_actions(text, answer, lang)
    kb = proactive_kb(actions, lang) or back_menu_kb(lang)
    is_quota = await deliver_ai_reply(loading, answer, lang=lang, prefix="🤖 ", reply_markup=kb)
    if not is_quota and user.memory_enabled:
        await add_memory(session, user.id, f"Q: {text[:200]}\nA: {answer[:400]}", module_id="ai_assistant")
