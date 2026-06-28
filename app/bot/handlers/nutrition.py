from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_nutrition import (
    nutrition_ai_kb,
    nutrition_cal_activity_kb,
    nutrition_cal_sex_kb,
    nutrition_cancel_kb,
    nutrition_grocery_kb,
    nutrition_module_kb,
    nutrition_water_kb,
)
from app.bot.states import NutritionStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.nutrition_service import (
    add_grocery_item,
    add_water,
    calculate_tdee,
    format_grocery_line,
    format_water_line,
    get_water_today,
    list_grocery_items,
    nutrition_submodule_description,
    parse_float,
    parse_int_amount,
    toggle_grocery_item,
)

router = Router()
AI_SUBS = frozenset({"diet", "calories", "recipes"})


@router.callback_query(F.data == "mod:nutrition")
async def nutrition_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "nutrition")
    await callback.message.edit_text(t(lang, "nut_module_intro"), reply_markup=nutrition_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:nutrition:"))
async def nutrition_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["nutrition"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "nutrition", submodule_id=sub_id)

    if sub_id == "grocery":
        await _show_grocery(callback.message, user, session, lang, edit=True)
    elif sub_id == "water":
        await _show_water(callback.message, user, session, lang, edit=True)
    elif sub_id in AI_SUBS:
        desc = nutrition_submodule_description(sub_id, lang)
        text = (
            f"🥗 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
            f"{desc}\n\n{t(lang, 'nut_ai_hint')}"
        )
        await callback.message.edit_text(text, reply_markup=nutrition_ai_kb("nutrition", sub_id, lang))
    await callback.answer()


async def _send(target, text: str, kb, edit: bool) -> None:
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_grocery(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_grocery_items(session, user.id)
    lines = [t(lang, "nut_grocery_title"), ""]
    if items:
        lines.extend(format_grocery_line(i) for i in items)
    else:
        lines.append(t(lang, "nut_empty"))
    await _send(target, "\n".join(lines), nutrition_grocery_kb(items, lang), edit)


async def _show_water(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    row = await get_water_today(session, user.id, user)
    lines = [t(lang, "nut_water_title"), "", format_water_line(row, lang), "", t(lang, "nut_water_hint")]
    await _send(target, "\n".join(lines), nutrition_water_kb(lang), edit)


@router.callback_query(F.data == "nut:groc:add")
async def nut_groc_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(NutritionStates.waiting_grocery_title)
    await callback.message.answer(t(user.language, "nut_grocery_title_prompt"), reply_markup=nutrition_cancel_kb(user.language))
    await callback.answer()


@router.message(NutritionStates.waiting_grocery_title)
async def nut_groc_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    await add_grocery_item(session, user_id=user.id, title=(message.text or "").strip(), profile_id=user.active_profile_id)
    await message.answer(t(lang, "nut_grocery_saved"))
    await _show_grocery(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data.startswith("nut:groc:toggle:"))
async def nut_groc_toggle(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    item_id = int((callback.data or "").split(":")[3])
    item = await toggle_grocery_item(session, user.id, item_id)
    if not item:
        await callback.answer(t(lang, "nut_not_found"), show_alert=True)
        return
    await _show_grocery(callback.message, user, session, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("nut:water:add:"))
async def nut_water_quick(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    ml = int((callback.data or "").split(":")[3])
    await add_water(session, user.id, user, ml)
    await _show_water(callback.message, user, session, user.language, edit=True)
    await callback.answer(t(user.language, "nut_water_added"))


@router.callback_query(F.data == "nut:water:custom")
async def nut_water_custom(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(NutritionStates.waiting_water_ml)
    await callback.message.answer(t(user.language, "nut_water_ml_prompt"), reply_markup=nutrition_cancel_kb(user.language))
    await callback.answer()


@router.message(NutritionStates.waiting_water_ml)
async def nut_water_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    ml = parse_int_amount(message.text or "")
    if ml is None:
        await message.answer(t(lang, "record_amount_error"))
        return
    await add_water(session, user.id, user, ml)
    await message.answer(t(lang, "nut_water_added"))
    await _show_water(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "nut:cal:calc")
async def nut_cal_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(NutritionStates.waiting_cal_weight)
    await callback.message.answer(t(user.language, "nut_cal_weight_prompt"), reply_markup=nutrition_cancel_kb(user.language))
    await callback.answer()


@router.message(NutritionStates.waiting_cal_weight)
async def nut_cal_weight(message: Message, state: FSMContext, user: User) -> None:
    weight = parse_float(message.text or "")
    if weight is None:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(nut_cal_weight=weight)
    await state.set_state(NutritionStates.waiting_cal_height)
    await message.answer(t(user.language, "nut_cal_height_prompt"), reply_markup=nutrition_cancel_kb(user.language))


@router.message(NutritionStates.waiting_cal_height)
async def nut_cal_height(message: Message, state: FSMContext, user: User) -> None:
    height = parse_float(message.text or "")
    if height is None:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(nut_cal_height=height)
    await state.set_state(NutritionStates.waiting_cal_age)
    await message.answer(t(user.language, "nut_cal_age_prompt"), reply_markup=nutrition_cancel_kb(user.language))


@router.message(NutritionStates.waiting_cal_age)
async def nut_cal_age(message: Message, state: FSMContext, user: User) -> None:
    age = parse_int_amount(message.text or "")
    if age is None or age > 120:
        await message.answer(t(user.language, "record_amount_error"))
        return
    await state.update_data(nut_cal_age=age)
    await message.answer(t(user.language, "nut_cal_sex_prompt"), reply_markup=nutrition_cal_sex_kb(user.language))


@router.callback_query(F.data.startswith("nut:cal:sex:"))
async def nut_cal_sex(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    sex = (callback.data or "").split(":")[3]
    await state.update_data(nut_cal_sex=sex)
    await callback.message.answer(t(user.language, "nut_cal_activity_prompt"), reply_markup=nutrition_cal_activity_kb(user.language))
    await callback.answer()


@router.callback_query(F.data.startswith("nut:cal:act:"))
async def nut_cal_finish(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    activity = (callback.data or "").split(":")[3]
    data = await state.get_data()
    tdee = calculate_tdee(
        weight_kg=float(data.get("nut_cal_weight") or 0),
        height_cm=float(data.get("nut_cal_height") or 0),
        age=int(data.get("nut_cal_age") or 0),
        sex=str(data.get("nut_cal_sex") or "male"),
        activity=activity,
    )
    await callback.message.answer(
        t(lang, "nut_cal_result", kcal=tdee),
        reply_markup=nutrition_ai_kb("nutrition", "calories", lang),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "nut:cancel")
async def nut_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "nut_module_intro"), reply_markup=nutrition_module_kb(user.language))
    await callback.answer()
