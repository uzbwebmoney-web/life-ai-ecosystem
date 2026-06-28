from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_education import education_ai_kb, education_module_kb
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.education_service import education_submodule_description
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "mod:education")
async def education_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "education")
    await callback.message.edit_text(t(lang, "edu_module_intro"), reply_markup=education_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:education:"))
async def education_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["education"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "education", submodule_id=sub_id)
    desc = education_submodule_description(sub_id, lang)
    text = (
        f"📚 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}\n\n{t(lang, 'edu_ai_hint')}"
    )
    await callback.message.edit_text(text, reply_markup=education_ai_kb("education", sub_id, lang))
    await callback.answer()
