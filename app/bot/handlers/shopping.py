from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_shopping import shopping_ai_kb, shopping_module_kb
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.shopping_service import shopping_submodule_description

router = Router()


@router.callback_query(F.data == "mod:shopping")
async def shopping_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "shopping")
    await callback.message.edit_text(t(lang, "shop_module_intro"), reply_markup=shopping_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:shopping:"))
async def shopping_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["shopping"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "shopping", submodule_id=sub_id)
    desc = shopping_submodule_description(sub_id, lang)
    text = (
        f"🛒 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}\n\n{t(lang, 'shop_ai_hint')}"
    )
    await callback.message.edit_text(text, reply_markup=shopping_ai_kb("shopping", sub_id, lang))
    await callback.answer()
