from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_health import (
    health_ai_kb,
    health_cancel_kb,
    health_diary_kb,
    health_docs_kb,
    health_med_item_kb,
    health_meds_kb,
    health_module_kb,
    health_visits_kb,
)
from app.bot.states import HealthStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.health_service import (
    HEALTH_VISIT_MODULE,
    METRIC_PRESSURE,
    METRIC_SUGAR,
    METRIC_WEIGHT,
    add_health_medication,
    add_health_metric,
    deactivate_health_medication,
    format_metric_line,
    format_medication_line,
    get_health_medication,
    health_submodule_description,
    list_health_documents,
    list_health_medications,
    list_health_metrics,
    list_health_visits,
    parse_pressure,
    parse_reminder_times,
    parse_single_value,
    update_health_medication,
)
from app.services.life_data import add_record, add_reminder, set_active_module

router = Router()

AI_SUBS = frozenset({"consultant", "symptoms", "tests", "exams", "medicines"})


@router.callback_query(F.data == "mod:health")
async def health_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "health")
    await callback.message.edit_text(t(lang, "health_module_intro"), reply_markup=health_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:health:"))
async def health_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["health"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "health", submodule_id=sub_id)

    if sub_id == "diary":
        await _show_diary(callback.message, user, session, lang, edit=True)
    elif sub_id == "med_reminders":
        await _show_meds(callback.message, user, session, lang, edit=True)
    elif sub_id == "visits":
        await _show_visits(callback.message, user, session, lang, edit=True)
    elif sub_id == "documents":
        await _show_docs(callback.message, user, session, lang, edit=True)
    else:
        desc = health_submodule_description(sub_id, lang)
        text = (
            f"🩺 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
            f"{desc}\n\n{t(lang, 'health_ai_hint')}"
        )
        await callback.message.edit_text(text, reply_markup=health_ai_kb("health", sub_id, lang))
    await callback.answer()


async def _show_diary(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    metrics = await list_health_metrics(session, user.id, limit=5)
    lines = [t(lang, "health_diary_title"), ""]
    if metrics:
        lines.append(t(lang, "health_diary_recent"))
        lines.extend(format_metric_line(m, lang) for m in metrics)
    else:
        lines.append(t(lang, "health_diary_empty"))
    text = "\n".join(lines)
    kb = health_diary_kb(lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_meds(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    meds = await list_health_medications(session, user.id)
    lines = [t(lang, "health_med_title"), ""]
    if meds:
        lines.append(t(lang, "health_med_count", count=len(meds)))
        lines.append(t(lang, "health_med_hint_multi"))
        lines.append("")
        lines.extend(format_medication_line(m, lang) for m in meds)
    else:
        lines.append(t(lang, "health_med_empty"))
    text = "\n".join(lines)
    kb = health_meds_kb(meds, lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


def _med_item_text(med, lang: str) -> str:
    times = med.reminder_times.replace(",", ", ")
    return (
        f"💊 <b>{med.name}</b>\n\n"
        f"{t(lang, 'health_med_dose')}: {med.dosage or '—'}\n"
        f"🕐 {times}"
    )


async def _show_visits(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    visits = await list_health_visits(session, user.id)
    lines = [t(lang, "health_visit_title"), ""]
    if visits:
        for v in visits:
            lines.append(f"• {v.due_at.strftime('%d.%m.%Y %H:%M')} — {v.title}")
    else:
        lines.append(t(lang, "health_visit_empty"))
    text = "\n".join(lines)
    kb = health_visits_kb(lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_docs(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    docs = await list_health_documents(session, user.id)
    lines = [t(lang, "health_doc_title"), "", t(lang, "health_doc_hint"), ""]
    if docs:
        for d in docs[:8]:
            lines.append(f"• <b>{d.title}</b> — {d.created_at.strftime('%d.%m.%Y')}")
    else:
        lines.append(t(lang, "health_doc_empty"))
    text = "\n".join(lines)
    kb = health_docs_kb(lang)
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("health:metric:"))
async def health_metric_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    metric_type = (callback.data or "").split(":")[2]
    await state.update_data(health_metric_type=metric_type)
    await state.set_state(HealthStates.waiting_metric_value)
    prompts = {
        METRIC_PRESSURE: t(lang, "health_enter_pressure"),
        METRIC_SUGAR: t(lang, "health_enter_sugar"),
        METRIC_WEIGHT: t(lang, "health_enter_weight"),
    }
    await callback.message.answer(prompts.get(metric_type, t(lang, "health_invalid_value")), reply_markup=health_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "health:diary:all")
async def health_diary_all(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    metrics = await list_health_metrics(session, user.id, limit=20)
    if not metrics:
        await callback.answer(t(lang, "health_diary_empty"), show_alert=True)
        return
    body = "\n".join(format_metric_line(m, lang) for m in metrics)
    await callback.message.answer(f"{t(lang, 'health_diary_title')}\n\n{body}", reply_markup=health_diary_kb(lang))
    await callback.answer()


@router.message(HealthStates.waiting_metric_value)
async def health_metric_value(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    data = await state.get_data()
    metric_type = str(data.get("health_metric_type") or METRIC_PRESSURE)
    raw = (message.text or "").strip()

    if metric_type == METRIC_PRESSURE:
        parsed = parse_pressure(raw)
        if not parsed:
            await message.answer(t(lang, "health_invalid_pressure"))
            return
        await state.update_data(health_primary=parsed[0], health_secondary=parsed[1])
    else:
        val = parse_single_value(raw)
        if val is None:
            await message.answer(t(lang, "health_invalid_value"))
            return
        await state.update_data(health_primary=val, health_secondary=None)

    await state.set_state(HealthStates.waiting_metric_notes)
    await message.answer(t(lang, "health_enter_notes"), reply_markup=health_cancel_kb(lang))


@router.message(HealthStates.waiting_metric_notes)
async def health_metric_notes(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    notes = (message.text or "").strip()
    if notes == "-":
        notes = ""
    await add_health_metric(
        session,
        user_id=user.id,
        metric_type=str(data.get("health_metric_type") or METRIC_PRESSURE),
        value_primary=float(data.get("health_primary") or 0),
        value_secondary=data.get("health_secondary"),
        notes=notes,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "health_metric_saved"), reply_markup=health_diary_kb(lang))
    await state.clear()


@router.callback_query(F.data == "health:med:add")
async def health_med_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HealthStates.waiting_med_name)
    await callback.message.answer(t(user.language, "health_med_name"), reply_markup=health_cancel_kb(user.language))
    await callback.answer()


@router.message(HealthStates.waiting_med_name)
async def health_med_name(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(t(lang, "health_med_name"))
        return
    await state.update_data(health_med_name=name)
    await state.set_state(HealthStates.waiting_med_dosage)
    await message.answer(t(lang, "health_med_dosage"), reply_markup=health_cancel_kb(lang))


@router.message(HealthStates.waiting_med_dosage)
async def health_med_dosage(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.update_data(health_med_dosage=(message.text or "").strip())
    await state.set_state(HealthStates.waiting_med_times)
    await message.answer(t(lang, "health_med_times"), reply_markup=health_cancel_kb(lang))


@router.message(HealthStates.waiting_med_times)
async def health_med_times(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    times = parse_reminder_times(message.text or "")
    if not times:
        await message.answer(t(lang, "health_med_times_error"))
        return
    data = await state.get_data()
    try:
        await add_health_medication(
            session,
            user_id=user.id,
            name=str(data.get("health_med_name") or ""),
            dosage=str(data.get("health_med_dosage") or ""),
            reminder_times=",".join(times),
            profile_id=user.active_profile_id,
        )
    except ValueError:
        await message.answer(t(lang, "health_med_times_error"))
        return
    meds = await list_health_medications(session, user.id)
    await message.answer(t(lang, "health_med_saved"), reply_markup=health_meds_kb(meds, lang))
    await state.clear()


@router.callback_query(F.data == "health:med:list")
async def health_med_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await _show_meds(callback.message, user, session, user.language, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("health:med:open:"))
async def health_med_open(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    med_id = int((callback.data or "").split(":")[3])
    med = await get_health_medication(session, user.id, med_id)
    if not med:
        await callback.answer(t(lang, "health_med_not_found"), show_alert=True)
        return
    await callback.message.edit_text(_med_item_text(med, lang), reply_markup=health_med_item_kb(med_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("health:med:edit:name:"))
async def health_med_edit_name_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    med_id = int((callback.data or "").split(":")[4])
    await state.update_data(health_edit_med_id=med_id)
    await state.set_state(HealthStates.waiting_med_edit_name)
    await callback.message.answer(t(lang, "health_med_edit_name_prompt"), reply_markup=health_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("health:med:edit:dose:"))
async def health_med_edit_dose_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    med_id = int((callback.data or "").split(":")[4])
    await state.update_data(health_edit_med_id=med_id)
    await state.set_state(HealthStates.waiting_med_edit_dosage)
    await callback.message.answer(t(lang, "health_med_edit_dose_prompt"), reply_markup=health_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("health:med:edit:times:"))
async def health_med_edit_times_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    med_id = int((callback.data or "").split(":")[4])
    await state.update_data(health_edit_med_id=med_id)
    await state.set_state(HealthStates.waiting_med_edit_times)
    await callback.message.answer(t(lang, "health_med_edit_times_prompt"), reply_markup=health_cancel_kb(lang))
    await callback.answer()


@router.message(HealthStates.waiting_med_edit_name)
async def health_med_edit_name_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(t(lang, "health_med_name"))
        return
    med_id = int((await state.get_data()).get("health_edit_med_id") or 0)
    med = await update_health_medication(session, user.id, med_id, name=name)
    if not med:
        await message.answer(t(lang, "health_med_not_found"))
        await state.clear()
        return
    await message.answer(
        f"{t(lang, 'health_med_updated')}\n\n{_med_item_text(med, lang)}",
        reply_markup=health_med_item_kb(med_id, lang),
    )
    await state.clear()


@router.message(HealthStates.waiting_med_edit_dosage)
async def health_med_edit_dose_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    med_id = int((await state.get_data()).get("health_edit_med_id") or 0)
    med = await update_health_medication(session, user.id, med_id, dosage=(message.text or "").strip())
    if not med:
        await message.answer(t(lang, "health_med_not_found"))
        await state.clear()
        return
    await message.answer(
        f"{t(lang, 'health_med_updated')}\n\n{_med_item_text(med, lang)}",
        reply_markup=health_med_item_kb(med_id, lang),
    )
    await state.clear()


@router.message(HealthStates.waiting_med_edit_times)
async def health_med_edit_times_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    times = parse_reminder_times(message.text or "")
    if not times:
        await message.answer(t(lang, "health_med_times_error"))
        return
    med_id = int((await state.get_data()).get("health_edit_med_id") or 0)
    try:
        med = await update_health_medication(session, user.id, med_id, reminder_times=",".join(times))
    except ValueError:
        await message.answer(t(lang, "health_med_times_error"))
        return
    if not med:
        await message.answer(t(lang, "health_med_not_found"))
        await state.clear()
        return
    await message.answer(
        f"{t(lang, 'health_med_updated')}\n\n{_med_item_text(med, lang)}",
        reply_markup=health_med_item_kb(med_id, lang),
    )
    await state.clear()


@router.callback_query(F.data.startswith("health:med:del:"))
async def health_med_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    med_id = int((callback.data or "").split(":")[3])
    ok = await deactivate_health_medication(session, user.id, med_id)
    if not ok:
        await callback.answer(t(lang, "health_med_not_found"), show_alert=True)
        return
    await _show_meds(callback.message, user, session, lang, edit=True)
    await callback.answer(t(lang, "health_med_removed"))


@router.callback_query(F.data == "health:visit:add")
async def health_visit_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HealthStates.waiting_visit_title)
    await callback.message.answer(t(user.language, "health_visit_name"), reply_markup=health_cancel_kb(user.language))
    await callback.answer()


@router.message(HealthStates.waiting_visit_title)
async def health_visit_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(health_visit_title=(message.text or "").strip())
    await state.set_state(HealthStates.waiting_visit_datetime)
    await message.answer(t(user.language, "health_visit_datetime"), reply_markup=health_cancel_kb(user.language))


@router.message(HealthStates.waiting_visit_datetime)
async def health_visit_datetime(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    title = str(data.get("health_visit_title") or t(lang, "health_visit_title"))
    try:
        due = datetime.strptime((message.text or "").strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(t(lang, "remind_date_error"))
        return
    await add_reminder(
        session,
        user_id=user.id,
        title=title,
        due_at=due,
        module_id=HEALTH_VISIT_MODULE,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "health_visit_saved"), reply_markup=health_visits_kb(lang))
    await state.clear()


@router.callback_query(F.data == "health:doc:add")
async def health_doc_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(HealthStates.waiting_doc_title)
    await callback.message.answer(t(user.language, "health_doc_hint"), reply_markup=health_cancel_kb(user.language))
    await callback.answer()


@router.message(HealthStates.waiting_doc_title)
async def health_doc_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (message.text or "").strip()
    if len(text) < 2:
        return
    await add_record(
        session,
        user_id=user.id,
        module_id="health",
        submodule_id="documents",
        title=text[:200],
        body=text,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "health_doc_saved"), reply_markup=health_docs_kb(lang))
    await state.clear()


@router.callback_query(F.data == "health:cancel")
async def health_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "main_menu").split("\n")[0], reply_markup=health_module_kb(user.language))
    await callback.answer()
