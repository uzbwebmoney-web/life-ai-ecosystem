from __future__ import annotations

import json
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ai_reply_ui import deliver_ai_reply
from app.bot.reply_menu import thinking_reply_markup
from app.bot.keyboards_agent import agent_confirm_kb
from app.bot.keyboards import back_menu_kb, dashboard_kb
from app.bot.states import AgentStates
from app.core.i18n import t
from app.models.entities import User
from app.services.agent.orchestrator import deserialize_plan, execute_agent_plan, run_agent, serialize_plan

router = Router()
logger = logging.getLogger(__name__)


async def handle_agent_message(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    text: str,
    *,
    photo_context: dict | None = None,
    intent=None,
) -> bool:
    """Run agent pipeline. Returns True if handled."""
    from app.services.unified_ai.intent_router import analyze_intent
    from app.services.unified_ai.suggestions import should_offer_save, smart_suggestions, unified_reply_kb

    lang = user.language
    loading = await message.answer(t(lang, "agent_working"), reply_markup=thinking_reply_markup(lang))
    try:
        result = await run_agent(
            session,
            user,
            text,
            bot=message.bot,
            lang=lang,
            photo_context=photo_context,
        )
        if result.pending and result.plan:
            await state.set_state(AgentStates.waiting_confirm)
            await state.update_data(agent_plan=json.dumps(serialize_plan(result.plan), ensure_ascii=False))
            await loading.edit_text(result.text, reply_markup=agent_confirm_kb(lang))
            return True

        resolved_intent = intent or analyze_intent(text, active_module=user.active_module_id)
        actions = smart_suggestions(resolved_intent, text, result.text, lang)
        offer_save = should_offer_save(resolved_intent, text, result.text, memory_enabled=user.memory_enabled)
        kb = unified_reply_kb(actions, lang, offer_save=offer_save) or back_menu_kb(lang)
        await deliver_ai_reply(loading, result.text, lang=lang, prefix="", reply_markup=kb)
        for data, filename, _mime in result.files:
            await message.answer_document(BufferedInputFile(data, filename=filename))
        await state.update_data(last_unified_q=text, last_unified_a=result.text[:2000])
        await state.clear()
        return True
    except Exception:
        logger.exception("Agent failed")
        await loading.edit_text(t(lang, "ai_request_failed"), reply_markup=back_menu_kb(lang))
        return True


@router.callback_query(F.data == "agent:confirm")
async def agent_confirm(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    lang = user.language
    data = await state.get_data()
    raw = data.get("agent_plan")
    if not raw:
        await callback.answer(t(lang, "agent_plan_expired"), show_alert=True)
        return
    plan = deserialize_plan(json.loads(raw))
    await callback.message.edit_text(t(lang, "agent_executing"))
    result = await execute_agent_plan(session, user, plan, bot=callback.bot, lang=lang, skip_confirm=True)
    await deliver_ai_reply(callback.message, result.text, lang=lang, reply_markup=dashboard_kb(lang))
    for file_data, filename, _ in result.files:
        await callback.message.answer_document(BufferedInputFile(file_data, filename=filename))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "agent:cancel")
async def agent_cancel(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    lang = user.language
    await state.clear()
    await callback.message.edit_text(t(lang, "agent_cancelled"), reply_markup=dashboard_kb(lang))
    await callback.answer()
