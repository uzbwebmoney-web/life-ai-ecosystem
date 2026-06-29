from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.dashboard_view import send_dashboard
from app.bot.handlers.ecosystem import _apply_household_join
from app.bot.hub_views import create_project_from_title, run_export, show_projects, show_subscription, show_today, show_workspace
from app.bot.keyboards import back_menu_kb, dashboard_kb, language_kb
from app.core.config import settings
from app.bot.states import AiChatStates, MemoryStates, ReminderStates
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.vault_lock_service import lock_vault_on_menu_exit

router = Router()

_SLASH = re.compile(r"^/(\w+)(?:@\w+)?(?:\s+(.*))?$", re.I)


async def _show_help(message: Message, user: User) -> None:
    from app.bot.keyboards import help_kb

    await message.answer(t(user.language, "help_text"), reply_markup=help_kb(user.language))


async def _show_lang(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "choose_language"), reply_markup=language_kb(lang))


async def _show_menu(message: Message, user: User, session: AsyncSession) -> None:
    lock_vault_on_menu_exit(user)
    await send_dashboard(message, user, session)


@router.message(F.text.regexp(_SLASH))
async def slash_command_redirect(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
) -> None:
    raw = (message.text or "").strip()
    match = _SLASH.match(raw)
    if not match:
        return
    cmd = match.group(1).lower()
    args = (match.group(2) or "").strip()
    lang = user.language

    if cmd == "start":
        return

    await state.clear()

    if cmd in {"menu", "home"}:
        await _show_menu(message, user, session)
        return
    if cmd == "today":
        await show_today(message, user, session)
        return
    if cmd == "project":
        if args:
            await create_project_from_title(message, user, session, args)
        else:
            await show_projects(message, user, session)
        return
    if cmd == "workspace":
        await show_workspace(message, user, session)
        return
    if cmd in {"subscription", "premium", "tariff"}:
        await show_subscription(message, user, session)
        return
    if cmd == "help":
        await _show_help(message, user)
        return
    if cmd == "lang":
        await _show_lang(message, user)
        return
    if cmd == "memory":
        await state.set_state(MemoryStates.waiting_save)
        await message.answer(t(lang, "memory_cmd"), reply_markup=back_menu_kb(lang))
        return
    if cmd == "remind":
        await state.set_state(ReminderStates.waiting_title)
        await message.answer(t(lang, "remind_format"), reply_markup=back_menu_kb(lang))
        return
    if cmd == "export":
        await run_export(message, user, session)
        return
    if cmd == "ask":
        await state.update_data(ai_module_hint="", ai_module_id="ai_assistant", ai_chat_history=[])
        await state.set_state(AiChatStates.waiting_question)
        from app.bot.keyboards import ai_chat_kb

        await message.answer(
            f"{t(lang, 'ai_assistant_title')}\n\n{t(lang, 'ai_assistant_ask')}",
            reply_markup=ai_chat_kb(lang),
        )
        return
    if cmd == "expense":
        await message.answer(t(lang, "use_buttons_expense"), reply_markup=dashboard_kb(lang))
        return
    if cmd == "oil":
        await set_active_module(session, user, "car", submodule_id="maintenance")
        await message.answer(t(lang, "cmd_oil_hint"), reply_markup=back_menu_kb(lang))
        return
    if cmd == "credit":
        from app.bot.handlers.finance import _show_loans

        await set_active_module(session, user, "finance", submodule_id="loans")
        await _show_loans(message, user, session, lang)
        return
    if cmd == "join" and args:
        await _apply_household_join(message, user, session, args)
        return
    if cmd == "admin":
        from app.bot.handlers.admin import _show_admin_menu

        if user.telegram_id in settings.admin_telegram_id_list:
            await _show_admin_menu(message, user.language, session)
            return

    await _show_menu(message, user, session)
    await message.answer(t(lang, "use_buttons_hint"))
