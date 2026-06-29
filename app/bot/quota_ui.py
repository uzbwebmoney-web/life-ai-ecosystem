from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.keyboards_subscription import quota_upgrade_kb
from app.core.i18n import t
from app.services.subscription_service import parse_insufficient_credits_reply


async def answer_quota_block(
    message: Message,
    text: str,
    *,
    lang: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Show quota/limit message with upgrade buttons."""
    _, body = parse_insufficient_credits_reply(text)
    kb = reply_markup or quota_upgrade_kb(lang)
    await message.answer(body, parse_mode="HTML", reply_markup=kb)


async def answer_quota_key(message: Message, key: str, *, lang: str) -> None:
    await answer_quota_block(message, t(lang, key), lang=lang)
