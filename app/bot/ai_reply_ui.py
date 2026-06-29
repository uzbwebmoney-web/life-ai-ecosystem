from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.keyboards_subscription import insufficient_credits_kb
from app.bot.message_ui import deliver_long_text
from app.services.subscription_service import parse_insufficient_credits_reply


async def deliver_ai_reply(
    anchor: Message,
    answer: str,
    *,
    lang: str,
    prefix: str = "",
    reply_markup: InlineKeyboardMarkup | None = None,
) -> bool:
    """Deliver AI text; return True if this was an insufficient-credits message (no voice)."""
    is_quota, body = parse_insufficient_credits_reply(answer)
    if is_quota:
        await deliver_long_text(anchor, body, reply_markup=insufficient_credits_kb(lang))
        return True
    text = f"{prefix}{body}" if prefix else body
    await deliver_long_text(anchor, text, reply_markup=reply_markup)
    return False
