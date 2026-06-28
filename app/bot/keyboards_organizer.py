from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import OrganizerItem


def organizer_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["organizer"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:organizer:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def organizer_tasks_kb(tasks: list[OrganizerItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "org_task_add"), callback_data="org:task:add")],
    ]
    for task in tasks[:12]:
        mark = "✅" if task.done else "⬜"
        rows.append(
            [InlineKeyboardButton(text=f"{mark} {task.title[:30]}", callback_data=f"org:task:toggle:{task.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:organizer")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def organizer_calendar_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "org_meet_add"), callback_data="org:meet:add"),
                InlineKeyboardButton(text=t(lang, "org_bday_add"), callback_data="org:bday:add"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:organizer")],
        ]
    )


def organizer_reminders_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "org_rem_add"), callback_data="org:rem:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:organizer")],
        ]
    )


def organizer_events_kb(event_type: str, lang: str = "ru") -> InlineKeyboardMarkup:
    add_cb = "org:meet:add" if event_type == "meeting" else "org:bday:add"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "org_add"), callback_data=add_cb)],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:organizer")],
        ]
    )


def organizer_notes_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "org_note_add"), callback_data="org:note:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:organizer")],
        ]
    )


def organizer_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="org:cancel")]]
    )
