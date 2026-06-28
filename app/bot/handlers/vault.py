from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_vault import (
    vault_cancel_kb,
    vault_delete_confirm_kb,
    vault_item_open_kb,
    vault_items_kb,
    vault_module_kb,
)
from app.bot.states import VaultStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.home_service import parse_amount
from app.services.life_data import set_active_module
from app.services.vault_service import (
    VAULT_FILE_SUBMODULES,
    add_vault_item,
    attach_file_to_record,
    delete_vault_item,
    format_vault_line,
    format_vault_text_view,
    get_vault_item,
    is_image_file,
    list_vault_items,
    parse_stored_file,
    record_has_file,
    vault_file_meta,
    vault_submodule_title_key,
)

router = Router()


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
    lines = [t(lang, title_key), "", t(lang, "vlt_list_hint"), ""]
    if sub_id == "passport":
        lines.append(t(lang, "vlt_passport_hint"))
        lines.append("")
    if records:
        from app.bot.keyboards_vault import VAULT_PAGE_SIZE

        start = page * VAULT_PAGE_SIZE
        chunk = records[start : start + VAULT_PAGE_SIZE]
        lines.extend(format_vault_line(r, sub_id, lang=lang) for r in chunk)
    else:
        lines.append(t(lang, "vlt_empty"))
    await _send(target, "\n".join(lines), vault_items_kb(records, sub_id, lang, page=page), edit)


async def _finalize_vault_item(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
    *,
    file_id: str | None = None,
    mime: str | None = None,
    kind: str | None = None,
) -> None:
    lang = user.language
    data = await state.get_data()
    sub_id = str(data.get("vlt_sub") or "notes")
    record_id = data.get("vlt_record_id")

    if record_id:
        record = await get_vault_item(session, user.id, int(record_id))
        if not record:
            await message.answer(t(lang, "vlt_not_found"))
            await state.clear()
            return
        if file_id:
            await attach_file_to_record(session, record, file_id=file_id, mime=mime, kind=kind)
        await message.answer(t(lang, "vlt_saved_with_file" if file_id else "vlt_saved"))
        await _show_items(message, user, session, lang, sub_id)
        await state.clear()
        return

    title = str(data.get("vlt_title") or t(lang, "vlt_default_title"))
    body = str(data.get("vlt_body") or "")
    amount = data.get("vlt_amount")
    meta = (
        vault_file_meta(sub_id, file_id, mime=mime, kind=kind)
        if file_id
        else None
    )
    await add_vault_item(
        session,
        user_id=user.id,
        submodule_id=sub_id,
        title=title,
        body=body,
        amount=float(amount) if amount is not None else None,
        profile_id=user.active_profile_id,
        meta_json=meta,
    )
    await message.answer(t(lang, "vlt_saved_with_file" if file_id else "vlt_saved"))
    await _show_items(message, user, session, lang, sub_id)
    await state.clear()


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


@router.callback_query(F.data.startswith("vlt:add:"))
async def vault_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    await state.clear()
    await state.update_data(vlt_sub=sub_id, vlt_record_id=None)
    await state.set_state(VaultStates.waiting_title)
    prompt = t(lang, "vlt_passport_title_prompt") if sub_id == "passport" else t(lang, "vlt_title_prompt")
    await callback.message.answer(prompt, reply_markup=vault_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("vlt:attach:"))
async def vault_attach_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    sub_id = parts[2]
    record_id = int(parts[3])
    await state.clear()
    await state.update_data(vlt_sub=sub_id, vlt_record_id=record_id)
    await state.set_state(VaultStates.waiting_attachment)
    await callback.message.answer(t(lang, "vlt_attach_prompt"), reply_markup=vault_cancel_kb(lang))
    await callback.answer()


@router.message(VaultStates.waiting_title)
async def vault_title(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(lang, "vlt_title_short"))
        return
    await state.update_data(vlt_title=title)
    data = await state.get_data()
    sub_id = str(data.get("vlt_sub") or "notes")
    if sub_id == "receipts":
        await state.set_state(VaultStates.waiting_amount)
        await message.answer(t(lang, "vlt_amount_prompt"), reply_markup=vault_cancel_kb(lang))
        return
    await state.set_state(VaultStates.waiting_body)
    prompt = t(lang, "vlt_passport_body_prompt") if sub_id == "passport" else t(lang, "vlt_body_prompt")
    await message.answer(prompt, reply_markup=vault_cancel_kb(lang))


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
async def vault_body(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    body = (message.text or "").strip()
    if body == "-":
        body = ""
    await state.update_data(vlt_body=body)
    await state.set_state(VaultStates.waiting_attachment)
    await message.answer(t(lang, "vlt_attach_prompt"), reply_markup=vault_cancel_kb(lang))


@router.message(VaultStates.waiting_attachment, F.photo)
async def vault_attach_photo(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    file_id = message.photo[-1].file_id
    await _finalize_vault_item(
        message, state, user, session, file_id=file_id, kind="photo"
    )


@router.message(VaultStates.waiting_attachment, F.document)
async def vault_attach_document(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    doc = message.document
    await _finalize_vault_item(
        message,
        state,
        user,
        session,
        file_id=doc.file_id,
        mime=doc.mime_type,
        kind="document",
    )


@router.message(VaultStates.waiting_attachment)
async def vault_attach_skip(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    if (message.text or "").strip() in ("-", "—", "/skip"):
        await _finalize_vault_item(message, state, user, session)
        return
    await message.answer(t(user.language, "vlt_attach_prompt"), reply_markup=vault_cancel_kb(user.language))


@router.callback_query(F.data.startswith("vlt:open:"))
async def vault_open(
    callback: CallbackQuery,
    bot: Bot,
    user: User,
    session: AsyncSession,
) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    sub_id = parts[2]
    record_id = int(parts[3])
    record = await get_vault_item(session, user.id, record_id)
    if not record:
        await callback.answer(t(lang, "vlt_not_found"), show_alert=True)
        return
    kb = vault_item_open_kb(sub_id, record, lang)
    await callback.message.answer(format_vault_text_view(record, lang), reply_markup=kb)
    stored = parse_stored_file(record)
    if stored:
        file_id, mime, kind = stored
        as_photo = is_image_file(mime, kind=kind)
        try:
            if as_photo:
                await bot.send_photo(chat_id=callback.message.chat.id, photo=file_id)
            else:
                await bot.send_document(chat_id=callback.message.chat.id, document=file_id)
        except Exception:
            try:
                if as_photo:
                    await bot.send_document(chat_id=callback.message.chat.id, document=file_id)
                else:
                    await bot.send_photo(chat_id=callback.message.chat.id, photo=file_id)
            except Exception:
                await callback.message.answer(t(lang, "vlt_file_expired"))
    await callback.answer()


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
