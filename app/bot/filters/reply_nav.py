from __future__ import annotations

from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message

from app.bot.keyboards import reply_keyboard_labels
from app.models.entities import User


class ReplyKeyboardNavFilter(Filter):
    async def __call__(self, message: Message, user: User) -> bool:
        text = (message.text or "").strip()
        return bool(text) and text in reply_keyboard_labels(user.language)
