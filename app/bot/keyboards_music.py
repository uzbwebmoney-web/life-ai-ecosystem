from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID


def music_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["music"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:music:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def music_sub_kb(sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if sub_id == "separate":
        rows.append(
            [
                InlineKeyboardButton(text=t(lang, "mus_btn_vocal"), callback_data="mus:mode:vocal"),
                InlineKeyboardButton(text=t(lang, "mus_btn_instrumental"), callback_data="mus:mode:instrumental"),
            ]
        )
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_both"), callback_data="mus:mode:both")])
    elif sub_id in {"analyze", "translate", "chords"}:
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_from_audio"), callback_data=f"mus:from_audio:{sub_id}")])
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_paste_text"), callback_data=f"mus:paste:{sub_id}")])
    elif sub_id == "lyrics":
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_send_track"), callback_data="mus:mode:lyrics")])
    elif sub_id == "collection":
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_view_collection"), callback_data="mus:collection:view")])
        rows.append([InlineKeyboardButton(text=t(lang, "mus_btn_save_last"), callback_data="mus:collection:save")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:music")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def music_after_lyrics_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "mus_btn_analyze"), callback_data="mus:quick:analyze"),
                InlineKeyboardButton(text=t(lang, "mus_btn_translate"), callback_data="mus:quick:translate"),
            ],
            [
                InlineKeyboardButton(text=t(lang, "mus_btn_chords"), callback_data="mus:quick:chords"),
                InlineKeyboardButton(text=t(lang, "mus_btn_save_collection"), callback_data="mus:collection:save"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:music")],
        ]
    )


def music_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="mus:cancel")],
        ]
    )
