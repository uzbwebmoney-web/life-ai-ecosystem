from __future__ import annotations

import html
import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.i18n import t
from app.models.entities import User

logger = logging.getLogger(__name__)


def _format_utc_offset(minutes: int | None) -> str:
    value = 300 if minutes is None else int(minutes)
    sign = "+" if value >= 0 else "-"
    total = abs(value)
    hours, mins = divmod(total, 60)
    return f"UTC{sign}{hours:02d}:{mins:02d}"


def _username_label(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return "—"


async def notify_admins_new_user(
    bot: Bot,
    user: User,
    *,
    telegram_lang: str | None = None,
    lang: str = "ru",
) -> None:
    if not settings.admin_new_user_notify:
        return
    admin_ids = settings.admin_telegram_id_list
    if not admin_ids:
        return

    tg_lang = (telegram_lang or "—").strip().upper() or "—"
    text = t(
        lang,
        "admin_notify_new_user",
        telegram_id=user.telegram_id,
        username=html.escape(_username_label(user)),
        bot_lang=(user.language or "ru").upper(),
        telegram_lang=tg_lang,
        utc_offset=_format_utc_offset(user.utc_offset_minutes),
        plan_id=user.plan_id or "free",
    )
    for admin_tid in admin_ids:
        try:
            await bot.send_message(admin_tid, text, parse_mode=ParseMode.HTML)
        except Exception as exc:
            logger.warning("Failed to notify admin %s about new user: %s", admin_tid, exc)


async def notify_admins_ai_request(
    bot: Bot,
    user: User,
    *,
    model: str,
    source: str,
    prompt_tokens: int,
    completion_tokens: int,
    preview: str | None = None,
    lang: str = "ru",
) -> None:
    if not settings.admin_ai_request_notify:
        return
    admin_ids = settings.admin_telegram_id_list
    if not admin_ids:
        return

    preview_text = (preview or "").strip()
    if len(preview_text) > 500:
        preview_text = preview_text[:497] + "..."
    text = t(
        lang,
        "admin_notify_ai_request",
        event=html.escape(source),
        telegram_id=user.telegram_id,
        username=html.escape(_username_label(user)),
        user_lang=(user.language or "ru").upper(),
        model=html.escape(model),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        preview=html.escape(preview_text) if preview_text else "—",
    )
    for admin_tid in admin_ids:
        try:
            await bot.send_message(admin_tid, text, parse_mode=ParseMode.HTML)
        except Exception as exc:
            logger.warning("Failed to notify admin %s about AI request: %s", admin_tid, exc)
