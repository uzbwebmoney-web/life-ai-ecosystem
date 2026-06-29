from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message

from app.bot.keyboards_support import support_admin_reply_kb, support_continue_kb
from app.core.config import settings
from app.core.i18n import t
from app.core.plans import PLANS, normalize_plan_id
from app.models.entities import User


def _user_label(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return f"id{user.telegram_id}"


def _plan_label(user: User, *, lang: str) -> str:
    plan = PLANS.get(normalize_plan_id(user.plan_id or "free"), PLANS["free"])
    return f"{plan.emoji} {t(lang, plan.name_key)}"


async def relay_user_message_to_admins(
    bot: Bot,
    message: Message,
    user: User,
    *,
    lang: str,
) -> bool:
    admin_ids = settings.admin_telegram_id_list
    if not admin_ids:
        return False

    header = t(
        lang,
        "support_admin_notify",
        user=_user_label(user),
        telegram_id=user.telegram_id,
        plan=_plan_label(user, lang=lang),
    )
    kb = support_admin_reply_kb(user.telegram_id, lang)
    delivered = False

    for admin_tid in admin_ids:
        try:
            if message.text:
                await bot.send_message(
                    admin_tid,
                    f"{header}\n\n{message.text}",
                    reply_markup=kb,
                )
            elif message.photo:
                await bot.send_photo(
                    admin_tid,
                    message.photo[-1].file_id,
                    caption=header,
                    reply_markup=kb,
                )
            elif message.document:
                await bot.send_document(
                    admin_tid,
                    message.document.file_id,
                    caption=header,
                    reply_markup=kb,
                )
            elif message.voice:
                await bot.send_voice(
                    admin_tid,
                    message.voice.file_id,
                    caption=header,
                    reply_markup=kb,
                )
            elif message.audio:
                await bot.send_audio(
                    admin_tid,
                    message.audio.file_id,
                    caption=header,
                    reply_markup=kb,
                )
            elif message.video:
                await bot.send_video(
                    admin_tid,
                    message.video.file_id,
                    caption=header,
                    reply_markup=kb,
                )
            else:
                await bot.send_message(admin_tid, header, reply_markup=kb)
                await bot.copy_message(
                    chat_id=admin_tid,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            delivered = True
        except Exception:
            continue

    return delivered


async def relay_admin_reply_to_user(
    bot: Bot,
    message: Message,
    *,
    user_telegram_id: int,
    lang: str,
) -> bool:
    header = t(lang, "support_user_from_admin")
    kb = support_continue_kb(lang)
    try:
        if message.text:
            await bot.send_message(user_telegram_id, f"{header}\n\n{message.text}", reply_markup=kb)
        elif message.photo:
            await bot.send_photo(
                user_telegram_id,
                message.photo[-1].file_id,
                caption=header,
                reply_markup=kb,
            )
        elif message.document:
            await bot.send_document(
                user_telegram_id,
                message.document.file_id,
                caption=header,
                reply_markup=kb,
            )
        elif message.voice:
            await bot.send_voice(
                user_telegram_id,
                message.voice.file_id,
                caption=header,
                reply_markup=kb,
            )
        elif message.audio:
            await bot.send_audio(
                user_telegram_id,
                message.audio.file_id,
                caption=header,
                reply_markup=kb,
            )
        elif message.video:
            await bot.send_video(
                user_telegram_id,
                message.video.file_id,
                caption=header,
                reply_markup=kb,
            )
        else:
            await bot.send_message(user_telegram_id, header, reply_markup=kb)
            await bot.copy_message(
                chat_id=user_telegram_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
        return True
    except Exception:
        return False
