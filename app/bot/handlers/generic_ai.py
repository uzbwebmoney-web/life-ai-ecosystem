from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_generic import generic_ai_kb, generic_module_kb
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.generic_ai_service import GENERIC_AI_MODULES, generic_module_intro, generic_submodule_description
from app.services.life_data import set_active_module

router = Router()


def _module_from_callback(data: str) -> str | None:
    parts = (data or "").split(":")
    if len(parts) < 2:
        return None
    if parts[0] == "mod":
        return parts[1]
    if parts[0] == "sub" and len(parts) >= 3:
        return parts[1]
    return None


@router.callback_query(lambda c: _module_from_callback(c.data or "") in GENERIC_AI_MODULES)
async def generic_module_entry(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = callback.data or ""
    if data.startswith("mod:"):
        module_id = data.split(":")[1]
        await set_active_module(session, user, module_id)
        mod = MODULE_BY_ID[module_id]
        text = f"{mod.emoji} <b>{mod.title(lang)}</b>\n\n{generic_module_intro(module_id, lang)}"
        await callback.message.edit_text(text, reply_markup=generic_module_kb(module_id, lang))
        await callback.answer()
        return
    if data.startswith("sub:"):
        _, module_id, sub_id = data.split(":", 2)
        mod = MODULE_BY_ID[module_id]
        sub = next((s for s in mod.submodules if s.id == sub_id), None)
        if not sub:
            await callback.answer(t(lang, "not_found"), show_alert=True)
            return
        await set_active_module(session, user, module_id, submodule_id=sub_id)
        desc = generic_submodule_description(module_id, sub_id, lang)
        text = (
            f"{mod.emoji} <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
            f"{desc}\n\n{t(lang, 'gen_ai_hint')}"
        )
        await callback.message.edit_text(text, reply_markup=generic_ai_kb(module_id, sub_id, lang))
        await callback.answer()
