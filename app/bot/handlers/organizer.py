from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_organizer import (
    organizer_calendar_kb,
    organizer_cancel_kb,
    organizer_events_kb,
    organizer_module_kb,
    organizer_notes_kb,
    organizer_reminders_kb,
    organizer_tasks_kb,
)
from app.bot.states import OrganizerStates
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.household_calendar_service import (
    add_household_event,
    format_household_event_line,
    list_household_calendar_events,
)
from app.services.organizer_service import (
    add_note,
    add_org_reminder,
    add_task,
    format_event_line,
    format_note_line,
    format_reminder_line,
    format_task_line,
    list_events_by_type,
    list_notes,
    list_org_reminders,
    list_tasks,
    parse_datetime,
    toggle_task,
)


@router.callback_query(F.data == "mod:organizer")
async def organizer_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "organizer")
    await callback.message.edit_text(t(lang, "org_module_intro"), reply_markup=organizer_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:calendar")
async def hub_calendar_redirect(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "organizer", submodule_id="calendar")
    await _show_calendar(callback.message, user, session, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("sub:organizer:"))
async def organizer_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    await set_active_module(session, user, "organizer", submodule_id=sub_id)
    if sub_id == "tasks":
        await _show_tasks(callback.message, user, session, lang, edit=True)
    elif sub_id == "calendar":
        await _show_calendar(callback.message, user, session, lang, edit=True)
    elif sub_id == "reminders":
        await _show_reminders(callback.message, user, session, lang, edit=True)
    elif sub_id == "birthdays":
        await _show_events(callback.message, user, session, lang, "birthday", edit=True)
    elif sub_id == "meetings":
        await _show_events(callback.message, user, session, lang, "meeting", edit=True)
    elif sub_id == "notes":
        await _show_notes(callback.message, user, session, lang, edit=True)
    await callback.answer()


async def _send(target, text: str, kb, edit: bool) -> None:
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_tasks(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    tasks = await list_tasks(session, user.id)
    lines = [t(lang, "org_tasks_title"), ""]
    if tasks:
        lines.extend(format_task_line(task, lang) for task in tasks)
    else:
        lines.append(t(lang, "org_empty"))
    await _send(target, "\n".join(lines), organizer_tasks_kb(tasks, lang), edit)


async def _show_calendar(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    if user.household_id:
        pairs = await list_household_calendar_events(session, user)
        lines = [t(lang, "family_calendar_title"), ""]
        if pairs:
            lines.extend(format_household_event_line(ev, author, lang) for ev, author in pairs)
        else:
            lines.append(t(lang, "org_empty"))
    else:
        from app.services.organizer_service import list_all_events

        events = await list_all_events(session, user.id)
        lines = [t(lang, "org_calendar_title"), ""]
        if events:
            lines.extend(format_event_line(e, lang) for e in events)
        else:
            lines.append(t(lang, "org_empty"))
    await _send(target, "\n".join(lines), organizer_calendar_kb(lang), edit)


async def _show_reminders(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    items = await list_org_reminders(session, user.id)
    lines = [t(lang, "org_reminders_title"), ""]
    if items:
        lines.extend(format_reminder_line(r) for r in items)
    else:
        lines.append(t(lang, "org_empty"))
    await _send(target, "\n".join(lines), organizer_reminders_kb(lang), edit)


async def _show_events(
    target, user: User, session: AsyncSession, lang: str, event_type: str, *, edit: bool = False
) -> None:
    title_key = "org_birthdays_title" if event_type == "birthday" else "org_meetings_title"
    events = await list_events_by_type(session, user.id, event_type)
    lines = [t(lang, title_key), ""]
    if events:
        lines.extend(format_event_line(e, lang) for e in events)
    else:
        lines.append(t(lang, "org_empty"))
    await _send(target, "\n".join(lines), organizer_events_kb(event_type, lang), edit)


async def _show_notes(target, user: User, session: AsyncSession, lang: str, *, edit: bool = False) -> None:
    notes = await list_notes(session, user.id)
    lines = [t(lang, "org_notes_title"), ""]
    if notes:
        lines.extend(format_note_line(n) for n in notes)
    else:
        lines.append(t(lang, "org_empty"))
    await _send(target, "\n".join(lines), organizer_notes_kb(lang), edit)


@router.callback_query(F.data == "org:task:add")
async def org_task_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(OrganizerStates.waiting_task_title)
    await callback.message.answer(t(user.language, "org_task_title_prompt"), reply_markup=organizer_cancel_kb(user.language))
    await callback.answer()


@router.message(OrganizerStates.waiting_task_title)
async def org_task_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(org_task_title=(message.text or "").strip())
    await state.set_state(OrganizerStates.waiting_task_due)
    await message.answer(t(user.language, "org_task_due_prompt"), reply_markup=organizer_cancel_kb(user.language))


@router.message(OrganizerStates.waiting_task_due)
async def org_task_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "").strip()
    due = None if raw in ("-", "") else parse_datetime(raw)
    if raw not in ("-", "") and due is None:
        await message.answer(t(lang, "org_date_error"))
        return
    data = await state.get_data()
    await add_task(
        session,
        user_id=user.id,
        title=str(data.get("org_task_title") or t(lang, "org_task_default")),
        due_at=due,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "org_task_saved"))
    await _show_tasks(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data.startswith("org:task:toggle:"))
async def org_task_toggle(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    task_id = int((callback.data or "").split(":")[3])
    task = await toggle_task(session, user.id, task_id)
    if not task:
        await callback.answer(t(lang, "org_not_found"), show_alert=True)
        return
    await _show_tasks(callback.message, user, session, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "org:note:add")
async def org_note_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(OrganizerStates.waiting_note_title)
    await callback.message.answer(t(user.language, "org_note_title_prompt"), reply_markup=organizer_cancel_kb(user.language))
    await callback.answer()


@router.message(OrganizerStates.waiting_note_title)
async def org_note_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(org_note_title=(message.text or "").strip())
    await state.set_state(OrganizerStates.waiting_note_body)
    await message.answer(t(user.language, "org_note_body_prompt"), reply_markup=organizer_cancel_kb(user.language))


@router.message(OrganizerStates.waiting_note_body)
async def org_note_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    body = (message.text or "").strip()
    if body == "-":
        body = ""
    data = await state.get_data()
    await add_note(
        session,
        user_id=user.id,
        title=str(data.get("org_note_title") or t(lang, "org_note_default")),
        body=body,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "org_note_saved"))
    await _show_notes(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "org:meet:add")
async def org_meet_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.update_data(org_event_type="meeting")
    await state.set_state(OrganizerStates.waiting_event_title)
    await callback.message.answer(t(user.language, "org_event_title_prompt"), reply_markup=organizer_cancel_kb(user.language))
    await callback.answer()


@router.callback_query(F.data == "org:bday:add")
async def org_bday_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.update_data(org_event_type="birthday")
    await state.set_state(OrganizerStates.waiting_event_title)
    await callback.message.answer(t(user.language, "org_bday_title_prompt"), reply_markup=organizer_cancel_kb(user.language))
    await callback.answer()


@router.message(OrganizerStates.waiting_event_title)
async def org_event_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(org_event_title=(message.text or "").strip())
    await state.set_state(OrganizerStates.waiting_event_datetime)
    await message.answer(t(user.language, "org_event_date_prompt"), reply_markup=organizer_cancel_kb(user.language))


@router.message(OrganizerStates.waiting_event_datetime)
async def org_event_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    starts = parse_datetime(message.text or "")
    if not starts:
        await message.answer(t(lang, "org_date_error"))
        return
    data = await state.get_data()
    event_type = str(data.get("org_event_type") or "meeting")
    await add_household_event(
        session,
        user,
        title=str(data.get("org_event_title") or t(lang, "org_event_default")),
        starts_at=starts,
        event_type=event_type,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "org_event_saved"))
    if event_type == "birthday":
        await _show_events(message, user, session, lang, "birthday")
    elif event_type == "meeting":
        await _show_events(message, user, session, lang, "meeting")
    else:
        await _show_calendar(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "org:rem:add")
async def org_rem_add(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(OrganizerStates.waiting_remind_title)
    await callback.message.answer(t(user.language, "org_rem_title_prompt"), reply_markup=organizer_cancel_kb(user.language))
    await callback.answer()


@router.message(OrganizerStates.waiting_remind_title)
async def org_rem_title(message: Message, state: FSMContext, user: User) -> None:
    await state.update_data(org_rem_title=(message.text or "").strip())
    await state.set_state(OrganizerStates.waiting_remind_datetime)
    await message.answer(t(user.language, "org_rem_date_prompt"), reply_markup=organizer_cancel_kb(user.language))


@router.message(OrganizerStates.waiting_remind_datetime)
async def org_rem_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    due = parse_datetime(message.text or "")
    if not due:
        await message.answer(t(lang, "org_date_error"))
        return
    data = await state.get_data()
    title = str(data.get("org_rem_title") or t(lang, "org_rem_default"))
    await add_org_reminder(
        session,
        user_id=user.id,
        title=title,
        due_at=due,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "org_rem_saved", title=title, when=due.strftime("%d.%m.%Y %H:%M")))
    await _show_reminders(message, user, session, lang)
    await state.clear()


@router.callback_query(F.data == "org:cancel")
async def org_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "org_module_intro"), reply_markup=organizer_module_kb(user.language))
    await callback.answer()
