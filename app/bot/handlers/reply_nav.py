from __future__ import annotations

from aiogram import Router
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.reply_nav import ReplyKeyboardNavFilter
from app.bot.handlers.dashboard_view import send_dashboard
from app.bot.keyboards import all_reply_menu_labels
from app.models.entities import User
from app.services.vault_lock_service import lock_vault_on_menu_exit

router = Router()


@router.message(ReplyKeyboardNavFilter())
async def reply_keyboard_nav(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
) -> None:
    text = (message.text or "").strip()
    if text not in all_reply_menu_labels():
        return
    await state.clear()
    lock_vault_on_menu_exit(user)
    await send_dashboard(message, user, session)
