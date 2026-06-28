from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import language_kb, main_menu_kb
from app.core.i18n import t
from app.models.entities import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "welcome"), reply_markup=main_menu_kb(lang))


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "welcome"), reply_markup=main_menu_kb(lang))


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    await message.answer(t(user.language, "choose_language"), reply_markup=language_kb(user.language))
