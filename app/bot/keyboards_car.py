from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import CarCompliance, CarMaintenanceItem


def car_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["car"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:car:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def car_ai_kb(sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:car:{sub_id}")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")],
        ]
    )


def car_panel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data="ai:car:panel_photo")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")],
        ]
    )


def car_service_kb(items: list[CarMaintenanceItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "car_service_add"), callback_data="car:maint:add")],
    ]
    for item in items[:12]:
        rows.append(
            [InlineKeyboardButton(text=f"📅 {item.title[:28]}", callback_data=f"car:maint:open:{item.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def car_maint_type_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    types = ("oil", "filter", "tires", "service", "other")
    rows = [
        [InlineKeyboardButton(text=t(lang, f"car_maint_{tp}"), callback_data=f"car:maint:type:{tp}")]
        for tp in types
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="car:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def car_maint_item_kb(item_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "car_maint_delete"), callback_data=f"car:maint:del:{item_id}")],
            [InlineKeyboardButton(text=t(lang, "car_back_list"), callback_data="car:service:list")],
        ]
    )


def car_reminders_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "car_maint_oil"), callback_data="car:maint:quick:oil"),
                InlineKeyboardButton(text=t(lang, "car_maint_filter"), callback_data="car:maint:quick:filter"),
            ],
            [InlineKeyboardButton(text=t(lang, "car_maint_tires"), callback_data="car:maint:quick:tires")],
            [InlineKeyboardButton(text=t(lang, "car_service_add"), callback_data="car:maint:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")],
        ]
    )


def car_compliance_kb(rows: list[CarCompliance], lang: str = "ru") -> InlineKeyboardMarkup:
    kb_rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=t(lang, "car_comp_add_insurance"), callback_data="car:comp:add:insurance"),
            InlineKeyboardButton(text=t(lang, "car_comp_add_inspection"), callback_data="car:comp:add:inspection"),
        ],
    ]
    for row in rows[:8]:
        kb_rows.append(
            [InlineKeyboardButton(text=f"🗑 {row.title[:26]}", callback_data=f"car:comp:del:{row.id}")]
        )
    kb_rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")])
    return InlineKeyboardMarkup(inline_keyboard=kb_rows)


def car_expenses_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "car_expenses_add"), callback_data="car:exp:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:car")],
        ]
    )


def car_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="car:cancel")]]
    )
