from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import language_kb, main_menu_kb
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import complete_onboarding, set_user_language

router = Router()


def onboarding_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "onb_start_btn"), callback_data="onb:finish")],
        ]
    )


async def _send_welcome(message: Message, user: User) -> None:
    lang = user.language
    if not user.onboarding_done:
        await message.answer(t(lang, "onb_welcome"), reply_markup=onboarding_kb(lang))
        return
    await message.answer(t(lang, "welcome"), reply_markup=main_menu_kb(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    await _send_welcome(message, user)


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User) -> None:
    await _send_welcome(message, user)


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    await message.answer(t(user.language, "choose_language"), reply_markup=language_kb(user.language))


@router.callback_query(lambda c: (c.data or "").startswith("onb:"))
async def onboarding_flow(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = callback.data or ""
    if data == "onb:finish":
        await complete_onboarding(session, user)
        await callback.message.edit_text(t(lang, "onb_done"))
        await callback.message.answer(t(lang, "welcome"), reply_markup=main_menu_kb(lang))
        await callback.answer()
        return
    if data.startswith("onb:lang:"):
        code = data.split(":")[2]
        await set_user_language(session, user, code)
        await callback.message.edit_text(t(user.language, "onb_welcome"), reply_markup=onboarding_kb(user.language))
        await callback.answer()
