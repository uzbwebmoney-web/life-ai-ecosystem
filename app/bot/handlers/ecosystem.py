from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import all_modules_kb, back_menu_kb, dashboard_kb, household_kb, sos_kb
from app.bot.keyboards_car import car_cancel_kb, car_maint_type_kb
from app.bot.keyboards_finance import finance_category_kb
from app.bot.keyboards_health import health_cancel_kb
from app.bot.states import HealthStates, MemoryStates, ScanStates
from app.core.i18n import t
from app.models.entities import User
from app.services.household_service import get_household_members, get_or_create_household, join_household
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
    members = await get_household_members(session, household.id)
    member_lines = []
    for member in members:
        u = (await session.execute(select(User).where(User.id == member.user_id))).scalar_one_or_none()
        if u:
            name = u.username or str(u.telegram_id)
            role = member.role
            member_lines.append(f"• {name} ({role})")
    members_text = "\n".join(member_lines) if member_lines else "—"
    text = t(lang, "household_info", code=household.invite_code) + f"\n\n<b>{t(lang, 'household_members_title')}</b>\n{members_text}"
    await callback.message.edit_text(text, reply_markup=household_kb(lang, household.invite_code))
    await callback.answer()


@router.callback_query(F.data == "hh:code")
async def hub_household_code(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    household = await get_or_create_household(session, user)
    await callback.answer(t(lang, "household_copy_code", code=household.invite_code), show_alert=True)


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
async def proactive_action(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    session: AsyncSession,
) -> None:
    lang = user.language
    action = (callback.data or "").split(":")[1]
    await state.clear()

    if action == "car_profile":
        await set_active_module(session, user, "car")
        await callback.message.answer(t(lang, "act_hint_car_profile"), reply_markup=dashboard_kb(lang))
    elif action == "car_service":
        await set_active_module(session, user, "car", submodule_id="service")
        await callback.message.answer(t(lang, "car_maint_pick_type"), reply_markup=car_maint_type_kb(lang))
    elif action == "car_insurance":
        await set_active_module(session, user, "car", submodule_id="compliance")
        await callback.message.answer(
            t(lang, "act_hint_car_insurance"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=t(lang, "ntf_open_module"), callback_data="sub:car:compliance")]
                ]
            ),
        )
    elif action in ("med_course", "med_remind"):
        sub = "med_reminders" if action == "med_remind" else "medicines"
        await set_active_module(session, user, "health", submodule_id=sub)
        await state.set_state(HealthStates.waiting_med_name)
        await callback.message.answer(t(lang, "health_med_name"), reply_markup=health_cancel_kb(lang))
    elif action == "travel_plan":
        await set_active_module(session, user, "travel", submodule_id="routes")
        await callback.message.answer(t(lang, "act_hint_travel_plan"), reply_markup=dashboard_kb(lang))
    elif action == "travel_passport":
        await set_active_module(session, user, "vault", submodule_id="passport")
        await callback.message.answer(t(lang, "act_hint_travel_passport"), reply_markup=dashboard_kb(lang))
    elif action == "save_expense":
        await set_active_module(session, user, "finance", submodule_id="expense")
        await callback.message.answer(t(lang, "fin_pick_category"), reply_markup=finance_category_kb(lang))
    elif action == "save_memory":
        await set_active_module(session, user, "ai_assistant")
        await state.set_state(MemoryStates.waiting_save)
        await callback.message.answer(t(lang, "memory_cmd"), reply_markup=back_menu_kb(lang))
    else:
        await callback.answer()
        return
    await callback.answer(t(lang, "act_done"))


@router.callback_query(F.data == "scan:expense")
async def scan_to_expense(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    amount = data.get("scan_amount")
    await set_active_module(session, user, "finance", submodule_id="expense")
    await state.update_data(fin_tx_type="expense", fin_category="other")
    from app.bot.states import FinanceStates
    from app.bot.keyboards_finance import finance_cancel_kb

    await state.set_state(FinanceStates.waiting_tx_title)
    hint = t(lang, "fin_tx_title_prompt")
    if amount:
        hint += f"\n\n💰 {t(lang, 'scan_amount_detected', amount=int(amount))}"
        await state.update_data(fin_tx_amount=float(amount))
    await callback.message.answer(hint, reply_markup=finance_cancel_kb(lang))
    await callback.answer()
