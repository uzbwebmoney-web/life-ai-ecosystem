from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_business import business_ai_kb, business_module_kb
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.business_service import business_submodule_description
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "mod:business")
async def business_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "business")
    await callback.message.edit_text(t(lang, "biz_module_intro"), reply_markup=business_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:business:"))
async def business_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["business"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "business", submodule_id=sub_id)
    desc = business_submodule_description(sub_id, lang)
    text = (
        f"💼 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}\n\n{t(lang, 'biz_ai_hint')}"
    )
    await callback.message.edit_text(text, reply_markup=business_ai_kb("business", sub_id, lang))
    await callback.answer()
