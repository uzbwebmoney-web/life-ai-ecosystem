from __future__ import annotations



from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



from app.core.i18n import t

from app.core.modules.catalog import MODULE_BY_ID

from app.models.entities import LifeRecord
from app.services.vault_service import record_has_file



VAULT_PAGE_SIZE = 8





def vault_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:

    mod = MODULE_BY_ID["vault"]

    rows = [

        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:vault:{sub.id}")]

        for sub in mod.submodules

    ]

    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)





def vault_items_kb(

    records: list[LifeRecord],

    submodule_id: str,

    lang: str = "ru",

    *,

    page: int = 0,

) -> InlineKeyboardMarkup:

    total_pages = max(1, (len(records) + VAULT_PAGE_SIZE - 1) // VAULT_PAGE_SIZE)

    page = max(0, min(page, total_pages - 1))

    start = page * VAULT_PAGE_SIZE

    chunk = records[start : start + VAULT_PAGE_SIZE]



    rows: list[list[InlineKeyboardButton]] = [

        [InlineKeyboardButton(text=t(lang, "vlt_add"), callback_data=f"vlt:add:{submodule_id}")],

    ]

    for record in chunk:
        label = record.title[:24]
        icon = "📎" if record_has_file(record) else "📝"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {label}",
                    callback_data=f"vlt:open:{submodule_id}:{record.id}",
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"vlt:del:{submodule_id}:{record.id}",
                ),
            ]
        )

    nav: list[InlineKeyboardButton] = []

    if page > 0:

        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"vlt:pg:{submodule_id}:{page - 1}"))

    if total_pages > 1:

        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="vlt:noop"))

    if page < total_pages - 1:

        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"vlt:pg:{submodule_id}:{page + 1}"))

    if nav:

        rows.append(nav)

    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:vault")])

    return InlineKeyboardMarkup(inline_keyboard=rows)





def vault_delete_confirm_kb(submodule_id: str, record_id: int, lang: str = "ru") -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(text=t(lang, "vlt_confirm_yes"), callback_data=f"vlt:delok:{submodule_id}:{record_id}"),

                InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data=f"vlt:pg:{submodule_id}:0"),

            ],

        ]

    )





def vault_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(

        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="vlt:cancel")]]

    )

