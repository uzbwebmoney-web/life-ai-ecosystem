from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import dashboard_kb
from app.core.i18n import t
from app.models.entities import User
from app.services.project_service import set_active_project

router = Router()


@router.callback_query(F.data.startswith("project:set:"))
async def project_set_active(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    pid = int((callback.data or "").split(":")[2])
    ok = await set_active_project(session, user, pid)
    if ok:
        await callback.message.edit_text(t(lang, "project_switched"), reply_markup=dashboard_kb(lang))
    await callback.answer()
