from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.admin import is_admin
from app.bot.keyboards import settings_kb
from app.bot.keyboards_support import support_user_kb
from app.bot.message_ui import safe_edit_text
from app.bot.states import AdminStates, SupportStates
from app.core.config import settings
from app.core.i18n import LANG_LABELS, t
from app.models.entities import User
from app.services.support_service import relay_admin_reply_to_user, relay_user_message_to_admins
from app.services.vault_lock_service import is_vault_protected

router = Router()


@router.callback_query(F.data == "sup:open")
async def support_open(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    lang = user.language
    if not settings.admin_telegram_id_list:
        await callback.answer(t(lang, "support_no_admins"), show_alert=True)
        return
    await state.set_state(SupportStates.chat_active)
    await safe_edit_text(
        callback.message,
        f"{t(lang, 'support_intro')}\n\n{t(lang, 'support_prompt')}",
        reply_markup=support_user_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "sup:exit")
async def support_exit(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    lang = user.language
    await state.clear()
    mem = "✅" if user.memory_enabled else "❌"
    voice = "✅" if user.voice_mode else "❌"
    vault_status = t(lang, "status_on") if is_vault_protected(user) else t(lang, "status_off")
    await safe_edit_text(
        callback.message,
        f"{t(lang, 'settings_title')}\n\n"
        f"{t(lang, 'settings_memory', status=mem)}\n"
        f"{t(lang, 'settings_voice', status=voice)}\n"
        f"{t(lang, 'settings_vault_lock', status=vault_status)}\n"
        f"{t(lang, 'settings_lang', label=LANG_LABELS.get(lang, lang.upper()))}\n\n"
        f"{t(lang, 'settings_tip')}\n\n"
        f"{t(lang, 'settings_extra')}",
        reply_markup=settings_kb(
            user.memory_enabled,
            user.voice_mode,
            lang,
            vault_locked=is_vault_protected(user),
            is_admin=is_admin(user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sup:reply:"))
async def support_admin_reply_start(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    if not is_admin(user):
        await callback.answer()
        return
    lang = user.language
    telegram_id = int((callback.data or "").split(":")[2])
    await state.set_state(AdminStates.waiting_support_reply)
    await state.update_data(support_user_telegram_id=telegram_id)
    label = f"id{telegram_id}"
    await callback.message.answer(
        f"{t(lang, 'support_admin_reply_ready', user=label, telegram_id=telegram_id)}\n\n"
        f"{t(lang, 'support_admin_reply_prompt')}",
    )
    await callback.answer()


@router.message(SupportStates.chat_active)
async def support_user_message(
    message: Message,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    lang = user.language
    if not settings.admin_telegram_id_list:
        await message.answer(t(lang, "support_no_admins"), reply_markup=support_user_kb(lang))
        await state.clear()
        return
    if message.text and message.text.startswith("/"):
        return
    ok = await relay_user_message_to_admins(bot, message, user, lang=lang)
    if ok:
        await message.answer(t(lang, "support_sent"), reply_markup=support_user_kb(lang))
    else:
        await message.answer(t(lang, "support_no_admins"), reply_markup=support_user_kb(lang))


@router.message(AdminStates.waiting_support_reply)
async def support_admin_reply_message(
    message: Message,
    user: User,
    state: FSMContext,
    bot: Bot,
    session: AsyncSession,
) -> None:
    if not is_admin(user):
        return
    lang = user.language
    data = await state.get_data()
    user_telegram_id = data.get("support_user_telegram_id")
    if not user_telegram_id:
        await state.clear()
        return
    if message.text and message.text.startswith("/"):
        if message.text.strip() == "/cancel":
            await state.clear()
            await message.answer(t(lang, "admin_btn_back"))
        return

    target_lang = lang
    from sqlalchemy import select

    row = await session.scalar(select(User).where(User.telegram_id == int(user_telegram_id)))
    if row:
        target_lang = row.language

    ok = await relay_admin_reply_to_user(
        bot,
        message,
        user_telegram_id=int(user_telegram_id),
        lang=target_lang,
    )
    if ok:
        await message.answer(t(lang, "support_admin_reply_sent"))
    else:
        await message.answer(f"⚠️ {user_telegram_id}")
    await state.clear()
