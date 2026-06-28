from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import LifeRecord


def vault_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["vault"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:vault:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def vault_items_kb(records: list[LifeRecord], submodule_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "vlt_add"), callback_data=f"vlt:add:{submodule_id}")],
    ]
    for record in records[:12]:
        label = record.title[:28]
        rows.append(
            [InlineKeyboardButton(text=f"🗑 {label}", callback_data=f"vlt:del:{submodule_id}:{record.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:vault")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def vault_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="vlt:cancel")]]
    )
