from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import dashboard_kb, settings_kb
from app.core.i18n import t
from app.models.entities import User

router = Router()

MODES = ("normal", "child", "elder")
STYLES = ("brief", "balanced", "detailed", "friendly")
LEVELS = ("beginner", "standard", "expert")


@router.callback_query(F.data.startswith("mode:ui:"))
async def set_ui_mode(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    mode = (callback.data or "").split(":")[2]
    if mode not in MODES:
        await callback.answer()
        return
    user.ui_mode = mode
    await session.commit()
    from app.bot.handlers.hub import _is_admin
    from app.services.vault_lock_service import is_vault_protected

    await callback.message.edit_text(
        t(lang, f"mode_ui_set_{mode}"),
        reply_markup=settings_kb(
            user.memory_enabled,
            user.voice_mode,
            lang,
            vault_locked=is_vault_protected(user),
            is_admin=_is_admin(user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mode:style:"))
async def set_style(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    style = (callback.data or "").split(":")[2]
    if style not in STYLES:
        await callback.answer()
        return
    user.response_style = style
    await session.commit()
    from app.bot.handlers.hub import _is_admin
    from app.services.vault_lock_service import is_vault_protected

    await callback.message.edit_text(
        t(lang, "mode_style_set", style=style),
        reply_markup=settings_kb(
            user.memory_enabled,
            user.voice_mode,
            lang,
            vault_locked=is_vault_protected(user),
            is_admin=_is_admin(user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mode:level:"))
async def set_level(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    level = (callback.data or "").split(":")[2]
    if level not in LEVELS:
        await callback.answer()
        return
    user.knowledge_level = level
    await session.commit()
    from app.bot.handlers.hub import _is_admin
    from app.services.vault_lock_service import is_vault_protected

    await callback.message.edit_text(
        t(lang, "mode_level_set", level=level),
        reply_markup=settings_kb(
            user.memory_enabled,
            user.voice_mode,
            lang,
            vault_locked=is_vault_protected(user),
            is_admin=_is_admin(user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "hub:modes")
async def hub_modes(callback: CallbackQuery, user: User) -> None:
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    lang = user.language
    rows = [
        [InlineKeyboardButton(text=t(lang, "mode_ui_normal"), callback_data="mode:ui:normal")],
        [InlineKeyboardButton(text=t(lang, "mode_ui_child"), callback_data="mode:ui:child")],
        [InlineKeyboardButton(text=t(lang, "mode_ui_elder"), callback_data="mode:ui:elder")],
        [InlineKeyboardButton(text=t(lang, "mode_style_brief"), callback_data="mode:style:brief")],
        [InlineKeyboardButton(text=t(lang, "mode_style_detailed"), callback_data="mode:style:detailed")],
        [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:settings")],
    ]
    await callback.message.edit_text(t(lang, "mode_menu_title"), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()
