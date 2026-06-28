from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_vault import vault_cancel_kb, vault_delete_confirm_kb, vault_items_kb, vault_module_kb
from app.bot.states import VaultStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.home_service import parse_amount
from app.services.life_data import set_active_module
from app.services.vault_service import (
    VAULT_FILE_SUBMODULES,
    add_vault_item,
    delete_vault_item,
    format_vault_line,
    list_vault_items,
    vault_submodule_title_key,
)

router = Router()


@router.callback_query(F.data == "mod:vault")
async def vault_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "vault")
    await callback.message.edit_text(t(lang, "vlt_module_intro"), reply_markup=vault_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:vault:"))
async def vault_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["vault"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "vault", submodule_id=sub_id)
    await _show_items(callback.message, user, session, lang, sub_id, edit=True)
    await callback.answer()


async def _send(target, text: str, kb, edit: bool) -> None:
    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def _show_items(
    target,
    user: User,
    session: AsyncSession,
    lang: str,
    sub_id: str,
    *,
    edit: bool = False,
    page: int = 0,
) -> None:
    records = await list_vault_items(session, user.id, sub_id)
    title_key = vault_submodule_title_key(sub_id)
    lines = [t(lang, title_key), ""]
    if sub_id == "passport":
        lines.append(t(lang, "vlt_passport_hint"))
        lines.append("")
    if sub_id in VAULT_FILE_SUBMODULES:
        lines.append(t(lang, "vlt_file_hint"))
        lines.append("")
    if records:
        from app.bot.keyboards_vault import VAULT_PAGE_SIZE

        start = page * VAULT_PAGE_SIZE
        chunk = records[start : start + VAULT_PAGE_SIZE]
        lines.extend(format_vault_line(r, sub_id) for r in chunk)
    else:
        lines.append(t(lang, "vlt_empty"))
    await _send(target, "\n".join(lines), vault_items_kb(records, sub_id, lang, page=page), edit)


@router.callback_query(F.data.startswith("vlt:add:"))
async def vault_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    await state.update_data(vlt_sub=sub_id)
    await state.set_state(VaultStates.waiting_title)
    prompt = t(lang, "vlt_passport_title_prompt") if sub_id == "passport" else t(lang, "vlt_title_prompt")
    await callback.message.answer(prompt, reply_markup=vault_cancel_kb(lang))
    await callback.answer()


@router.message(VaultStates.waiting_title)
async def vault_title(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.update_data(vlt_title=(message.text or "").strip())
    data = await state.get_data()
    sub_id = str(data.get("vlt_sub") or "notes")
    if sub_id == "passport":
        await state.set_state(VaultStates.waiting_body)
        await message.answer(t(lang, "vlt_passport_body_prompt"), reply_markup=vault_cancel_kb(lang))
        return
    if sub_id == "receipts":
        await state.set_state(VaultStates.waiting_amount)
        await message.answer(t(lang, "vlt_amount_prompt"), reply_markup=vault_cancel_kb(lang))
        return
    await state.set_state(VaultStates.waiting_body)
    await message.answer(t(lang, "vlt_body_prompt"), reply_markup=vault_cancel_kb(lang))


@router.message(VaultStates.waiting_amount)
async def vault_amount(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    raw = (message.text or "").strip()
    amount = None if raw in ("-", "") else parse_amount(raw)
    if raw not in ("-", "") and amount is None:
        await message.answer(t(lang, "vlt_amount_error"))
        return
    await state.update_data(vlt_amount=amount)
    await state.set_state(VaultStates.waiting_body)
    await message.answer(t(lang, "vlt_body_prompt"), reply_markup=vault_cancel_kb(lang))


@router.message(VaultStates.waiting_body)
async def vault_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    body = (message.text or "").strip()
    if body == "-":
        body = ""
    data = await state.get_data()
    sub_id = str(data.get("vlt_sub") or "notes")
    title = str(data.get("vlt_title") or t(lang, "vlt_default_title"))
    amount = data.get("vlt_amount")
    await add_vault_item(
        session,
        user_id=user.id,
        submodule_id=sub_id,
        title=title,
        body=body,
        amount=float(amount) if amount is not None else None,
        profile_id=user.active_profile_id,
    )
    await message.answer(t(lang, "vlt_saved"))
    await _show_items(message, user, session, lang, sub_id)
    await state.clear()


@router.callback_query(F.data.startswith("vlt:pg:"))
async def vault_page(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    parts = (callback.data or "").split(":")
    sub_id = parts[2]
    page = int(parts[3])
    await _show_items(callback.message, user, session, user.language, sub_id, edit=True, page=page)
    await callback.answer()


@router.callback_query(F.data == "vlt:noop")
async def vault_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("vlt:del:"))
async def vault_delete_confirm(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    sub_id = parts[2]
    record_id = int(parts[3])
    await callback.message.edit_text(
        t(lang, "vlt_delete_confirm"),
        reply_markup=vault_delete_confirm_kb(sub_id, record_id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("vlt:delok:"))
async def vault_delete(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    sub_id = parts[2]
    record_id = int(parts[3])
    ok = await delete_vault_item(session, user.id, record_id)
    if not ok:
        await callback.answer(t(lang, "vlt_not_found"), show_alert=True)
        return
    await _show_items(callback.message, user, session, lang, sub_id, edit=True)
    await callback.answer(t(lang, "vlt_deleted"))


@router.callback_query(F.data == "vlt:cancel")
async def vault_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await callback.message.answer(t(user.language, "vlt_module_intro"), reply_markup=vault_module_kb(user.language))
    await callback.answer()
