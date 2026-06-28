from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.dashboard_view import edit_dashboard, send_dashboard
from app.bot.keyboards import dashboard_kb, help_kb, onboarding_kb, start_language_kb
from app.core.i18n import LANG_LABELS, t
from app.models.entities import User
from app.services.life_data import complete_onboarding, mark_welcome_pending, set_user_language

router = Router()


async def _show_modules_menu(message: Message, user: User, session: AsyncSession) -> None:
    await send_dashboard(message, user, session)


async def _show_welcome(message: Message, lang: str) -> None:
    await message.answer(t(lang, "onb_welcome"), reply_markup=onboarding_kb(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, session: AsyncSession) -> None:
    if user.onboarding_done:
        await _show_modules_menu(message, user, session)
        return
    if user.welcome_pending:
        await _show_welcome(message, user.language)
        return
    await message.answer(t(user.language, "start_pick_language"), reply_markup=start_language_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User, session: AsyncSession) -> None:
    await _show_modules_menu(message, user, session)


@router.message(Command("help"))
async def cmd_help(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "help_text"), reply_markup=help_kb(lang))


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    from app.bot.keyboards import language_kb

    await message.answer(t(user.language, "choose_language"), reply_markup=language_kb(user.language))


@router.callback_query(lambda c: (c.data or "").startswith("start:lang:"))
async def start_pick_language(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    code = (callback.data or "").split(":")[2]
    new_lang = await set_user_language(session, user, code)
    await mark_welcome_pending(session, user)
    await callback.message.edit_text(t(new_lang, "language_changed", label=LANG_LABELS[new_lang]))
    await callback.message.answer(t(new_lang, "onb_welcome"), reply_markup=onboarding_kb(new_lang))
    await callback.answer()


@router.callback_query(lambda c: (c.data or "") == "start:begin")
async def start_begin(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await complete_onboarding(session, user)
    await callback.message.edit_text(t(lang, "onb_done"))
    await edit_dashboard(callback, user, session)
    await callback.answer()
