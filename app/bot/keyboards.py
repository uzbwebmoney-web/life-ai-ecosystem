from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import LANG_LABELS, SUPPORTED_LANGUAGES, t
from app.core.modules.catalog import CATEGORIES, MODULES, MODULE_BY_ID, ModuleDef
from app.models.entities import FamilyProfile


def start_language_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=LANG_LABELS[code], callback_data=f"start:lang:{code}")]
        for code in SUPPORTED_LANGUAGES
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def onboarding_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_open_menu"), callback_data="start:begin")],
        ]
    )


def _module_btn(mod: ModuleDef, lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=f"{mod.emoji} {mod.title(lang)}",
        callback_data=f"mod:{mod.id}",
    )


def dashboard_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "btn_sos"), callback_data="hub:sos")],
    ]
    pair: list[InlineKeyboardButton] = []
    for mod in MODULES:
        pair.append(_module_btn(mod, lang))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append(
        [
            InlineKeyboardButton(text=t(lang, "btn_notifications"), callback_data="hub:notifications"),
            InlineKeyboardButton(text=t(lang, "btn_calendar"), callback_data="hub:calendar"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(text=t(lang, "btn_search"), callback_data="hub:search"),
            InlineKeyboardButton(text=t(lang, "btn_scan"), callback_data="hub:scan"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(text=t(lang, "btn_dashboard"), callback_data="hub:dashboard"),
            InlineKeyboardButton(text=t(lang, "btn_settings"), callback_data="hub:settings"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return dashboard_kb(lang)


def all_modules_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for mod in MODULES:
        pair.append(_module_btn(mod, lang))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def sos_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    from app.services.sos_service import SOS_TOPICS

    rows = [
        [InlineKeyboardButton(text=t(lang, f"sos_btn_{topic}"), callback_data=f"sos:{topic}")]
        for topic in SOS_TOPICS
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def household_kb(lang: str, invite_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "household_copy_code", code=invite_code), callback_data="hh:code")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def modules_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    pair: list[InlineKeyboardButton] = []
    for mod in MODULES:
        pair.append(_module_btn(mod, lang))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return home_menu_kb(lang)


def language_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=LANG_LABELS[code], callback_data=f"set:lang:{code}")]
        for code in SUPPORTED_LANGUAGES
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_kb(memory_on: bool, voice_on: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    mem_label = t(lang, "btn_memory_on") if memory_on else t(lang, "btn_memory_off")
    voice_label = t(lang, "btn_voice_on") if voice_on else t(lang, "btn_voice_off")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=mem_label, callback_data="set:memory")],
            [InlineKeyboardButton(text=voice_label, callback_data="set:voice")],
            [
                InlineKeyboardButton(text=t(lang, "btn_search"), callback_data="hub:search"),
                InlineKeyboardButton(text=t(lang, "btn_notifications"), callback_data="hub:notifications"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_language"), callback_data="hub:language")],
            [InlineKeyboardButton(text=t(lang, "btn_family_profiles"), callback_data="hub:family")],
            [InlineKeyboardButton(text=t(lang, "btn_household"), callback_data="hub:household")],
            [InlineKeyboardButton(text=t(lang, "btn_help"), callback_data="hub:help")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def family_kb(profiles: list[FamilyProfile], active_id: int | None, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for profile in profiles:
        mark = "✅ " if profile.id == active_id else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark}{profile.name} ({profile.relation})",
                    callback_data=f"fam:switch:{profile.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_add_profile"), callback_data="fam:add")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def family_relation_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "family_rel_self"), callback_data="fam:rel:self"),
                InlineKeyboardButton(text=t(lang, "family_rel_spouse"), callback_data="fam:rel:spouse"),
            ],
            [
                InlineKeyboardButton(text=t(lang, "family_rel_child"), callback_data="fam:rel:child"),
                InlineKeyboardButton(text=t(lang, "family_rel_parent"), callback_data="fam:rel:parent"),
            ],
            [InlineKeyboardButton(text=t(lang, "family_rel_pet"), callback_data="fam:rel:pet")],
            [InlineKeyboardButton(text=t(lang, "family_rel_other"), callback_data="fam:rel:other")],
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="hub:family")],
        ]
    )


def categories_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    from app.core.i18n import category_title

    rows = [
        [InlineKeyboardButton(text=category_title(lang, idx), callback_data=f"cat:{idx}")]
        for idx in range(len(CATEGORIES))
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def category_modules_kb(category_idx: int, lang: str = "ru") -> InlineKeyboardMarkup:
    _, module_ids = CATEGORIES[category_idx]
    rows: list[list[InlineKeyboardButton]] = []
    for mid in module_ids:
        mod = MODULE_BY_ID[mid]
        rows.append([InlineKeyboardButton(text=f"{mod.emoji} {mod.title(lang)}", callback_data=f"mod:{mod.id}")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_categories"), callback_data="hub:categories")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def module_kb(mod: ModuleDef, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for sub in mod.submodules:
        rows.append([InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:{mod.id}:{sub.id}")])
    rows.append(
        [
            InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{mod.id}"),
            InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{mod.id}"),
        ]
    )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def submodule_kb(module_id: str, submodule_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_ask_ai"),
                    callback_data=f"ai:{module_id}:{submodule_id}",
                ),
                InlineKeyboardButton(
                    text=t(lang, "btn_add_record_full"),
                    callback_data=f"rec:{module_id}:{submodule_id}",
                ),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data=f"mod:{module_id}")],
        ]
    )


def back_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")]]
    )


def record_saved_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_search_record"), callback_data="hub:search")],
            [InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")],
        ]
    )


def help_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_open_menu"), callback_data="hub:menu")],
        ]
    )
