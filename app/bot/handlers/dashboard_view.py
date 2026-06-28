from __future__ import annotations

from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import dashboard_kb
from app.models.entities import User
from app.services.dashboard_service import build_dashboard


def _display_name(source: Message | CallbackQuery) -> str | None:
    user = source.from_user
    if not user:
        return None
    return user.first_name or user.full_name


async def send_dashboard(message: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (await build_dashboard(session, user, lang, display_name=_display_name(message))).text
    await message.answer(text, reply_markup=dashboard_kb(lang))


async def edit_dashboard(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (await build_dashboard(session, user, lang, display_name=_display_name(callback))).text
    await callback.message.edit_text(text, reply_markup=dashboard_kb(lang))
