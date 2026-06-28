from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import all_modules_kb, back_menu_kb, dashboard_kb, household_kb, sos_kb
from app.bot.states import ScanStates
from app.core.i18n import t
from app.models.entities import User
from app.services.household_service import get_or_create_household, join_household
from app.services.life_data import set_active_module
from app.services.sos_service import sos_menu_text, sos_topic_text

router = Router()


@router.callback_query(F.data == "hub:all_modules")
async def hub_all_modules(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    await callback.message.edit_text(t(lang, "all_modules_pick"), reply_markup=all_modules_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:scan")
async def hub_scan_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(ScanStates.waiting_photo)
    await callback.message.answer(t(user.language, "scan_prompt"), reply_markup=back_menu_kb(user.language))
    await callback.answer()


@router.callback_query(F.data == "hub:sos")
async def hub_sos_menu(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    await callback.message.edit_text(sos_menu_text(lang), reply_markup=sos_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sos:"))
async def hub_sos_topic(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    topic = (callback.data or "").split(":")[1]
    await callback.message.edit_text(sos_topic_text(lang, topic), reply_markup=sos_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:household")
async def hub_household(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    household = await get_or_create_household(session, user)
    text = t(lang, "household_info", code=household.invite_code)
    await callback.message.edit_text(text, reply_markup=household_kb(lang, household.invite_code))
    await callback.answer()


@router.message(Command("join"))
async def cmd_join_household(message: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    code = (message.text or "").replace("/join", "", 1).strip()
    if not code:
        await message.answer(t(lang, "household_join_usage"))
        return
    ok, reason = await join_household(session, user, code)
    if not ok:
        await message.answer(t(lang, f"household_join_{reason}"))
        return
    await message.answer(t(lang, "household_join_ok"), reply_markup=dashboard_kb(lang))


@router.callback_query(F.data.startswith("act:"))
async def proactive_action(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    action = (callback.data or "").split(":")[1]
    routes = {
        "car_profile": ("car", None, "act_hint_car_profile"),
        "car_service": ("car", "service", "act_hint_car_service"),
        "car_insurance": ("car", "compliance", "act_hint_car_insurance"),
        "med_course": ("health", "medicines", "act_hint_med_course"),
        "med_remind": ("health", "med_reminders", "act_hint_med_remind"),
        "travel_plan": ("travel", "routes", "act_hint_travel_plan"),
        "travel_passport": ("vault", "passport", "act_hint_travel_passport"),
        "save_expense": ("finance", "expense", "act_hint_save_expense"),
        "save_memory": ("ai_assistant", None, "act_hint_save_memory"),
    }
    if action not in routes:
        await callback.answer()
        return
    module_id, sub_id, hint_key = routes[action]
    await set_active_module(session, user, module_id, submodule_id=sub_id)
    await callback.message.answer(t(lang, hint_key), reply_markup=dashboard_kb(lang))
    await callback.answer(t(lang, "act_done"))
