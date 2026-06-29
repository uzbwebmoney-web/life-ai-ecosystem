from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.dashboard_view import edit_dashboard, send_dashboard
from app.bot.keyboards import dashboard_kb, help_kb, onboarding_kb, start_language_kb
from app.core.i18n import LANG_LABELS, t
from app.core.plans import TRIAL_DAYS, WELCOME_AI_BONUS
from app.models.entities import User
from app.services.life_data import complete_onboarding, mark_welcome_pending, set_user_language
from app.services.vault_lock_service import lock_vault_on_menu_exit

router = Router()


async def _show_modules_menu(message: Message, user: User, session: AsyncSession) -> None:
    await send_dashboard(message, user, session)


async def _show_welcome(message: Message, lang: str) -> None:
    from app.core.plans import TRIAL_DAYS

    await message.answer(t(lang, "onb_welcome", days=TRIAL_DAYS), reply_markup=onboarding_kb(lang))


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, session: AsyncSession) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("ref_"):
        from app.services.subscription_service import apply_referral

        if await apply_referral(session, user, parts[1][4:]):
            await message.answer(t(user.language, "sub_referral_applied"))
    if user.onboarding_done:
        await _show_modules_menu(message, user, session)
        return
    if user.welcome_pending:
        await _show_welcome(message, user.language)
        return
    await message.answer(t(user.language, "start_pick_language"), reply_markup=start_language_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User, session: AsyncSession) -> None:
    lock_vault_on_menu_exit(user)
    await _show_modules_menu(message, user, session)


@router.message(Command("help"))
async def cmd_help(message: Message, user: User) -> None:
    lang = user.language
    await message.answer(t(lang, "help_text"), reply_markup=help_kb(lang))


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    from app.bot.keyboards import language_kb

    await message.answer(t(user.language, "choose_language"), reply_markup=language_kb(user.language))


@router.callback_query(lambda c: (c.data or "").startswith("start:lang:"))
async def start_pick_language(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    code = (callback.data or "").split(":")[2]
    new_lang = await set_user_language(session, user, code)
    await mark_welcome_pending(session, user)
    await callback.message.edit_text(t(new_lang, "language_changed", label=LANG_LABELS[new_lang]))
    await callback.message.answer(t(new_lang, "onb_welcome", days=TRIAL_DAYS), reply_markup=onboarding_kb(new_lang))
    await callback.answer()


@router.callback_query(lambda c: (c.data or "") == "start:begin")
async def start_begin(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await complete_onboarding(session, user)
    await callback.message.edit_text(t(lang, "onb_done"))
    await callback.message.answer(t(lang, "sub_trial_welcome", days=TRIAL_DAYS, bonus=WELCOME_AI_BONUS))
    await edit_dashboard(callback, user, session)
    from app.services.admin_notify_service import notify_admins_new_user

    await notify_admins_new_user(
        callback.bot,
        user,
        telegram_lang=callback.from_user.language_code if callback.from_user else None,
    )
    await callback.answer()
