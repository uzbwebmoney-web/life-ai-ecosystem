from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_vault import vault_module_kb, vault_unlock_kb
from app.bot.states import VaultLockStates
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import set_active_module
from app.services.vault_lock_service import (
    is_vault_protected,
    is_vault_unlocked,
    record_vault_unlock_failure,
    unlock_vault,
    vault_unlock_rate_limited,
    verify_vault_password,
)


async def require_vault_unlock(
    user: User,
    state: FSMContext,
    lang: str,
    pending: str,
    *,
    reply: Message | CallbackQuery,
) -> bool:
    if not is_vault_protected(user) or is_vault_unlocked(user):
        return True
    await state.set_state(VaultLockStates.waiting_unlock)
    await state.update_data(vlt_pending=pending)
    target = reply.message if isinstance(reply, CallbackQuery) else reply
    await target.answer(t(lang, "vlt_lock_prompt"), reply_markup=vault_unlock_kb(lang))
    if isinstance(reply, CallbackQuery):
        await reply.answer()
    return False


async def resume_vault_pending(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    pending: str,
) -> None:
    from app.bot.handlers.vault import _show_items

    lang = user.language
    await state.clear()
    if pending.startswith("sub:vault:"):
        sub_id = pending.split(":")[2]
        await set_active_module(session, user, "vault", submodule_id=sub_id)
        await _show_items(message, user, session, lang, sub_id)
        return
    await set_active_module(session, user, "vault")
    await message.answer(t(lang, "vlt_module_intro"), reply_markup=vault_module_kb(lang))


async def try_unlock_vault(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    password: str,
) -> bool:
    lang = user.language
    if vault_unlock_rate_limited(user.id):
        await message.answer(t(lang, "vlt_lock_rate_limited"))
        try:
            await message.delete()
        except Exception:
            pass
        return False
    if not verify_vault_password(user, password):
        record_vault_unlock_failure(user.id)
        await message.answer(t(lang, "vlt_lock_wrong"))
        try:
            await message.delete()
        except Exception:
            pass
        return False
    unlock_vault(user)
    await session.commit()
    try:
        await message.delete()
    except Exception:
        pass
    data = await state.get_data()
    pending = str(data.get("vlt_pending") or "mod:vault")
    await message.answer(t(lang, "vlt_lock_unlocked"))
    await resume_vault_pending(message, user, session, state, pending)
    return True
