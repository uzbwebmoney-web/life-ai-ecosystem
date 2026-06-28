from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import NutritionGroceryItem


def nutrition_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["nutrition"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:nutrition:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def nutrition_ai_kb(module_id: str, sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub_id}"),
            InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{module_id}:{sub_id}"),
        ],
    ]
    if sub_id == "calories":
        rows.insert(0, [InlineKeyboardButton(text=t(lang, "nut_cal_calc"), callback_data="nut:cal:calc")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:nutrition")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def nutrition_grocery_kb(items: list[NutritionGroceryItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "nut_grocery_add"), callback_data="nut:groc:add")],
    ]
    for item in items[:12]:
        mark = "✅" if item.done else "⬜"
        rows.append(
            [InlineKeyboardButton(text=f"{mark} {item.title[:30]}", callback_data=f"nut:groc:toggle:{item.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:nutrition")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def nutrition_water_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="+250 ml", callback_data="nut:water:add:250"),
                InlineKeyboardButton(text="+500 ml", callback_data="nut:water:add:500"),
            ],
            [InlineKeyboardButton(text=t(lang, "nut_water_custom"), callback_data="nut:water:custom")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:nutrition")],
        ]
    )


def nutrition_cal_sex_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "nut_cal_male"), callback_data="nut:cal:sex:male"),
                InlineKeyboardButton(text=t(lang, "nut_cal_female"), callback_data="nut:cal:sex:female"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="nut:cancel")],
        ]
    )


def nutrition_cal_activity_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "nut_act_sedentary"), callback_data="nut:cal:act:sedentary")],
            [InlineKeyboardButton(text=t(lang, "nut_act_light"), callback_data="nut:cal:act:light")],
            [InlineKeyboardButton(text=t(lang, "nut_act_moderate"), callback_data="nut:cal:act:moderate")],
            [InlineKeyboardButton(text=t(lang, "nut_act_active"), callback_data="nut:cal:act:active")],
            [InlineKeyboardButton(text=t(lang, "nut_act_very"), callback_data="nut:cal:act:very")],
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="nut:cancel")],
        ]
    )


def nutrition_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="nut:cancel")]]
    )
