from __future__ import annotations

from aiogram.filters import Filter
from aiogram.types import Message

from app.bot.keyboards import all_reply_menu_labels


class ReplyKeyboardNavFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        text = (message.text or "").strip()
        return bool(text) and text in all_reply_menu_labels()
