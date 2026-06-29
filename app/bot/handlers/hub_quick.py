from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import ai_chat_kb, back_menu_kb
from app.bot.states import AiChatStates, MemoryStates, ProjectStates, ReminderStates
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import set_active_module

router = Router()


@router.callback_query(F.data == "hub:today")
async def hub_today(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await show_today(callback, user, session, edit=True)
    await callback.answer()


@router.callback_query(F.data == "hub:projects")
async def hub_projects(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await show_projects(callback, user, session, edit=True)
    await callback.answer()


@router.callback_query(F.data == "hub:workspace")
async def hub_workspace(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await show_workspace(callback, user, session, edit=True)
    await callback.answer()


@router.callback_query(F.data == "hub:memory")
async def hub_memory(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(MemoryStates.waiting_save)
    await callback.message.answer(t(lang, "memory_cmd"), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:remind")
async def hub_remind(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(ReminderStates.waiting_title)
    await callback.message.answer(t(lang, "remind_format"), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:export")
async def hub_export(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await run_export(callback.message, user, session)
    await callback.answer()


@router.callback_query(F.data == "hub:expense")
async def hub_expense(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    from app.bot.handlers.finance import finance_category_kb

    lang = user.language
    await set_active_module(session, user, "finance", submodule_id="expense")
    await callback.message.answer(t(lang, "fin_pick_category"), reply_markup=finance_category_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:oil")
async def hub_oil(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "car", submodule_id="maintenance")
    await callback.message.answer(t(lang, "cmd_oil_hint"), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:ask")
async def hub_ask(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.update_data(ai_module_hint="", ai_module_id="ai_assistant", ai_chat_history=[])
    await state.set_state(AiChatStates.waiting_question)
    await callback.message.answer(
        f"{t(lang, 'ai_assistant_title')}\n\n{t(lang, 'ai_assistant_ask')}",
        reply_markup=ai_chat_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "hub:subscription")
async def hub_subscription(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await show_subscription(callback.message, user, session)
    await callback.answer()


@router.callback_query(F.data == "project:new")
async def project_new(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(ProjectStates.waiting_title)
    await callback.message.answer(t(lang, "project_title_prompt"), reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.message(ProjectStates.waiting_title)
async def project_title_input(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    title = (message.text or "").strip()
    if len(title) < 2:
        await message.answer(t(user.language, "project_title_short"))
        return
    await create_project_from_title(message, user, session, title)
    await state.clear()

