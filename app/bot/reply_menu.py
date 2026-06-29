from __future__ import annotations

from aiogram.types import Message

from app.bot.keyboards import main_reply_kb


async def refresh_reply_menu(message: Message, lang: str) -> None:
    """Ensure the persistent reply-keyboard menu button is visible."""
    await message.answer("\u2800", reply_markup=main_reply_kb(lang))


def thinking_reply_markup(lang: str):
    """Reply keyboard shown while AI is working (persists after edit)."""
    return main_reply_kb(lang)
