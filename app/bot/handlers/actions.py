from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb
from app.bot.states import AiChatStates, MemoryStates, RecordStates, ReminderStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.intent_router import module_hint
from app.services.life_data import add_memory, add_record, add_reminder, search_memory, set_active_module

router = Router()


@router.callback_query(F.data.startswith("ai:"))
async def ai_from_module(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    module_id = parts[1] if len(parts) > 1 else "ai_assistant"
    sub_id = parts[2] if len(parts) > 2 else ""
    if module_id in MODULE_BY_ID:
        await set_active_module(session, user, module_id, submodule_id=sub_id or None)
    mod = MODULE_BY_ID.get(module_id)
    hint = module_hint(module_id, sub_id or None, lang=lang)
    await state.update_data(ai_module_hint=hint, ai_module_id=module_id, ai_submodule_id=sub_id)
    await state.set_state(AiChatStates.waiting_question)
    mod_title = mod.title(lang) if mod else "AI"
    if sub_id and mod:
        sub = next((s for s in mod.submodules if s.id == sub_id), None)
        if sub:
            mod_title = f"{mod_title} → {sub.title(lang)}"
    await callback.message.answer(t(lang, "ai_ask_module", module=mod_title))
    await callback.answer()


@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.update_data(ai_module_hint="", ai_module_id="ai_assistant")
    await state.set_state(AiChatStates.waiting_question)
    await message.answer(f"{t(lang, 'ai_assistant_title')}\n\n{t(lang, 'ai_assistant_ask')}")


@router.message(AiChatStates.waiting_question)
async def ai_question(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (message.text or "").strip()
    if not text:
        return
    data = await state.get_data()
    hint = str(data.get("ai_module_hint") or "")
    module_id = str(data.get("ai_module_id") or "ai_assistant")
    memory_ctx = ""
    if user.memory_enabled:
        entries = await search_memory(session, user.id, text, limit=3)
        if entries:
            memory_ctx = "\n".join(e.content for e in entries)
    loading = await message.answer(t(lang, "ai_thinking"))
    answer = await ask_ai(user_message=text, module_hint=hint, memory_context=memory_ctx, language=lang)
    await loading.edit_text(f"🤖 {answer}")
    if user.memory_enabled:
        await add_memory(
            session,
            user.id,
            f"Q: {text[:200]}\nA: {answer[:400]}",
            module_id=module_id,
            profile_id=user.active_profile_id,
        )
    await state.clear()


@router.callback_query(F.data.startswith("rec:"))
async def record_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    parts = (callback.data or "").split(":")
    module_id = parts[1]
    sub_id = parts[2] if len(parts) > 2 else "notes"
    await state.update_data(rec_module=module_id, rec_sub=sub_id)
    await state.set_state(RecordStates.waiting_text)
    mod = MODULE_BY_ID.get(module_id)
    mod_title = mod.title(lang) if mod else module_id
    await callback.message.answer(f"{t(lang, 'record_new', module=mod_title)}\n\n{t(lang, 'record_send')}")
    await callback.answer()


@router.message(RecordStates.waiting_text)
async def record_text(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (message.text or "").strip()
    if not text:
        return
    data = await state.get_data()
    module_id = str(data.get("rec_module") or "vault")
    await state.update_data(rec_title=text[:200], rec_body=text)
    if module_id == "finance":
        await state.set_state(RecordStates.waiting_amount)
        await message.answer(t(lang, "record_amount"))
        return
    await _save_record(message, state, user, session)


@router.message(RecordStates.waiting_amount)
async def record_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "0").replace(",", ".").strip()
    try:
        amount = float(raw)
    except ValueError:
        await message.answer(t(lang, "record_amount_error"))
        return
    await state.update_data(rec_amount=amount if amount else None)
    await _save_record(message, state, user, session)


async def _save_record(
    message: Message,
    state: FSMContext,
    user: User,
    session: AsyncSession,
) -> None:
    lang = user.language
    data = await state.get_data()
    module_id = str(data.get("rec_module") or "vault")
    sub_id = str(data.get("rec_sub") or "notes")
    title = str(data.get("rec_title") or "Запись")
    body = str(data.get("rec_body") or "")
    amount = data.get("rec_amount")

    await add_record(
        session,
        user_id=user.id,
        module_id=module_id,
        submodule_id=sub_id,
        title=title,
        body=body,
        amount=float(amount) if amount is not None else None,
        currency="UZS" if amount else None,
        profile_id=user.active_profile_id,
    )

    await message.answer(t(lang, "record_saved"), reply_markup=back_menu_kb(lang))
    await state.clear()


@router.message(Command("memory"))
async def cmd_memory(message: Message, state: FSMContext, user: User) -> None:
    await state.set_state(MemoryStates.waiting_save)
    await message.answer(t(user.language, "memory_cmd"))


@router.message(MemoryStates.waiting_save)
async def memory_save(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    text = (message.text or "").strip()
    if not text:
        return
    await add_memory(session, user.id, text, profile_id=user.active_profile_id)
    await message.answer(t(lang, "memory_saved"), reply_markup=back_menu_kb(lang))
    await state.clear()


@router.message(Command("remind"))
async def cmd_remind(message: Message, state: FSMContext, user: User) -> None:
    await state.set_state(ReminderStates.waiting_title)
    await message.answer(t(user.language, "remind_format"))


@router.message(ReminderStates.waiting_title)
async def remind_parse(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    raw = (message.text or "").strip()
    if "|" in raw:
        title, dt_raw = [p.strip() for p in raw.split("|", 1)]
        try:
            due = datetime.strptime(dt_raw, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer(t(lang, "remind_date_error"))
            return
        await add_reminder(session, user_id=user.id, title=title, due_at=due, profile_id=user.active_profile_id)
        await message.answer(
            t(lang, "remind_created", title=title, when=due.strftime("%d.%m.%Y %H:%M")),
            reply_markup=back_menu_kb(lang),
        )
        await state.clear()
        return
    await state.update_data(remind_title=raw)
    await state.set_state(ReminderStates.waiting_datetime)
    await message.answer(t(lang, "remind_datetime"))


@router.message(ReminderStates.waiting_datetime)
async def remind_datetime(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    data = await state.get_data()
    title = str(data.get("remind_title") or t(lang, "remind_default_title"))
    try:
        due = datetime.strptime((message.text or "").strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(t(lang, "remind_date_error"))
        return
    await add_reminder(session, user_id=user.id, title=title, due_at=due, profile_id=user.active_profile_id)
    await message.answer(
        t(lang, "remind_created", title=title, when=due.strftime("%d.%m.%Y %H:%M")),
        reply_markup=back_menu_kb(lang),
    )
    await state.clear()
