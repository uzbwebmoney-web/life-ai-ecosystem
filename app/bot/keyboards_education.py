from __future__ import annotations



import re



from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



from app.core.i18n import t





def education_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:

    from app.core.modules.catalog import MODULE_BY_ID



    mod = MODULE_BY_ID["education"]

    rows = [

        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:education:{sub.id}")]

        for sub in mod.submodules

    ]

    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)





def education_ai_kb(module_id: str, sub_id: str, lang: str = "ru") -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub_id}"),

                InlineKeyboardButton(text=t(lang, "btn_add_record"), callback_data=f"rec:{module_id}:{sub_id}"),

            ],

            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:education")],

        ]

    )





def study_spec_kb(lang: str = "ru") -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(text=t(lang, "edu_spec_5_pdf"), callback_data="edu:spec:5:pdf"),

                InlineKeyboardButton(text=t(lang, "edu_spec_10_pdf"), callback_data="edu:spec:10:pdf"),

            ],

            [

                InlineKeyboardButton(text=t(lang, "edu_spec_3_chat"), callback_data="edu:spec:3:chat"),

                InlineKeyboardButton(text=t(lang, "edu_spec_15_chat"), callback_data="edu:spec:15:chat"),

            ],

            [

                InlineKeyboardButton(text=t(lang, "edu_spec_5_docx"), callback_data="edu:spec:5:docx"),

            ],

            [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="edu:spec:cancel")],

        ]

    )





def study_followup_kb(module_id: str, sub_id: str | None, lang: str = "ru") -> InlineKeyboardMarkup:

    sub = sub_id or "notes"

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(text=t(lang, "edu_btn_export_pdf"), callback_data="edu:exp:pdf"),

                InlineKeyboardButton(text=t(lang, "edu_btn_export_docx"), callback_data="edu:exp:docx"),

            ],

            [

                InlineKeyboardButton(text=t(lang, "edu_btn_export_txt"), callback_data="edu:exp:txt"),

                InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data=f"ai:{module_id}:{sub}"),

            ],

            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data=f"mod:{module_id}")],

        ]

    )





def module_reply_kb(

    module_id: str,

    submodule_id: str | None,

    lang: str = "ru",

) -> InlineKeyboardMarkup:

    from app.bot.keyboards import module_kb, submodule_kb

    from app.core.modules.catalog import MODULE_BY_ID



    if module_id == "education":

        return study_followup_kb(module_id, submodule_id, lang)

    mod = MODULE_BY_ID.get(module_id)

    if submodule_id and mod:

        return submodule_kb(module_id, submodule_id, lang)

    if mod:

        return module_kb(mod, lang)

    from app.bot.keyboards import back_menu_kb



    return back_menu_kb(lang)


