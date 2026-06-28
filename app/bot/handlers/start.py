from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import language_kb, modules_menu_kb, start_language_kb
from app.core.i18n import LANG_LABELS, t
from app.models.entities import User
from app.services.life_data import complete_onboarding, set_user_language

router = Router()


async def _show_modules_menu(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "main_menu"), reply_markup=modules_menu_kb(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    if not user.onboarding_done:
        await message.answer(t(user.language, "start_pick_language"), reply_markup=start_language_kb())
        return
    await _show_modules_menu(message, user)


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User) -> None:
    await _show_modules_menu(message, user)


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    await message.answer(t(user.language, "choose_language"), reply_markup=language_kb(user.language))


@router.callback_query(lambda c: (c.data or "").startswith("start:lang:"))
async def start_pick_language(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    code = (callback.data or "").split(":")[2]
    new_lang = await set_user_language(session, user, code)
    await complete_onboarding(session, user)
    await callback.message.edit_text(t(new_lang, "language_changed", label=LANG_LABELS[new_lang]))
    await callback.message.answer(t(new_lang, "main_menu"), reply_markup=modules_menu_kb(new_lang))
    await callback.answer()
