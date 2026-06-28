from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_legal import legal_ai_kb, legal_module_kb
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.legal_service import legal_submodule_description
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "mod:legal")
async def legal_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "legal")
    await callback.message.edit_text(t(lang, "leg_module_intro"), reply_markup=legal_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:legal:"))
async def legal_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["legal"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "legal", submodule_id=sub_id)
    desc = legal_submodule_description(sub_id, lang)
    text = (
        f"⚖️ <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}\n\n{t(lang, 'leg_ai_hint')}"
    )
    await callback.message.edit_text(text, reply_markup=legal_ai_kb("legal", sub_id, lang))
    await callback.answer()
