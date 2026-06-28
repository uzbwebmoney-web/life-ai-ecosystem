from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers.dashboard_view import edit_dashboard
from app.bot.keyboards import (
    back_menu_kb,
    categories_kb,
    category_modules_kb,
    dashboard_kb,
    help_kb,
    language_kb,
    main_menu_kb,
    module_kb,
    settings_kb,
    submodule_kb,
)
from app.bot.keyboards_ecosystem import ecosystem_features_kb, notifications_kb
from app.bot.states import MemoryStates
from app.core.i18n import LANG_LABELS, category_title, t
from app.core.modules.catalog import CATEGORIES, MODULE_BY_ID
from app.core.modules.ui_texts import module_example_text, module_hint_text
from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.ecosystem_service import (
    build_search_ai_context,
    format_notifications_list,
    format_unified_search,
    list_unified_notifications,
    unified_search,
)
from app.services.life_data import (
    clear_active_module,
    dashboard_stats,
    get_active_profile,
    set_active_module,
    set_user_language,
    toggle_memory,
    toggle_voice_mode,
)

router = Router()


def _lang(user: User) -> str:
    return user.language


@router.callback_query(F.data == "hub:menu")
async def hub_menu(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    await clear_active_module(session, user)
    await edit_dashboard(callback, user, session)
    await callback.answer()


@router.callback_query(F.data == "hub:dashboard")
async def hub_dashboard(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    stats = await dashboard_stats(session, user.id)
    profile = await get_active_profile(session, user)
    balance = stats["income"] - stats["expense"]
    text = t(lang, "dashboard_title") + "\n\n" + t(
        lang,
        "dashboard_body",
        profile=profile.name if profile else "—",
        profiles=stats["profiles"],
        credits=stats["credits"],
        records=stats["records"],
        events=stats["events"],
        reminders=stats["reminders"],
        memory=stats["memory"],
        income=stats["income"],
        expense=stats["expense"],
        balance=balance,
        modules=len(MODULE_BY_ID),
    )
    await callback.message.edit_text(text, reply_markup=back_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:categories")
async def hub_categories(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    await callback.message.edit_text(
        t(lang, "all_modules", count=len(MODULE_BY_ID)),
        reply_markup=categories_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def hub_category(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    idx = int((callback.data or "").split(":")[1])
    await callback.message.edit_text(
        t(lang, "pick_module", category=category_title(lang, idx)),
        reply_markup=category_modules_kb(idx, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mod:"))
async def open_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    module_id = (callback.data or "").split(":")[1]
    mod = MODULE_BY_ID.get(module_id)
    if not mod:
        await callback.answer(t(lang, "module_not_found"), show_alert=True)
        return
    await set_active_module(session, user, module_id)
    subs = "\n".join(f"• {s.title(lang)}" for s in mod.submodules[:8])
    extra = f"\n{t(lang, 'module_more', count=len(mod.submodules) - 8)}" if len(mod.submodules) > 8 else ""
    hint = module_hint_text(module_id, lang)
    example = module_example_text(module_id, lang)
    example_line = f"\n{t(lang, 'module_example_label')} {example}\n" if example else "\n"
    text = (
        f"{mod.emoji} <b>{mod.title(lang)}</b>\n"
        f"<i>{category_title(lang, _module_category_idx(module_id))}</i>\n\n"
        f"{hint}{example_line}\n"
        f"{t(lang, 'module_ask_here')}\n"
        f"{t(lang, 'module_or_pick')}"
    )
    await callback.message.edit_text(text, reply_markup=module_kb(mod, lang))
    await callback.answer()


def _module_category_idx(module_id: str) -> int:
    for idx, (_, ids) in enumerate(CATEGORIES):
        if module_id in ids:
            return idx
    return 0


@router.callback_query(F.data.startswith("sub:"))
async def open_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    _, module_id, sub_id = (callback.data or "").split(":", 2)
    mod = MODULE_BY_ID.get(module_id)
    if not mod:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, module_id, submodule_id=sub_id)
    text = (
        f"{mod.emoji} <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{t(lang, 'submodule_ask', sub=sub.title(lang))}\n\n"
        f"{t(lang, 'submodule_also')}"
    )
    await callback.message.edit_text(text, reply_markup=submodule_kb(module_id, sub_id, lang))
    await callback.answer()


@router.callback_query(F.data == "hub:notifications")
@router.callback_query(F.data == "hub:reminders")
async def hub_notifications(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    items = await list_unified_notifications(session, user.id, lang)
    text = format_notifications_list(items, lang)
    await callback.message.edit_text(text, reply_markup=notifications_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:ecosystem")
async def hub_ecosystem(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    mem = "✅" if user.memory_enabled else "❌"
    voice = "✅" if user.voice_mode else "❌"
    text = t(lang, "eco_features_intro", memory=mem, voice=voice)
    await callback.message.edit_text(text, reply_markup=ecosystem_features_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:search")
async def hub_search_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = _lang(user)
    await state.set_state(MemoryStates.waiting_search)
    await callback.message.answer(
        f"{t(lang, 'search_title')}\n\n{t(lang, 'search_hint')}",
        reply_markup=back_menu_kb(lang),
    )
    await callback.answer()


@router.message(MemoryStates.waiting_search)
async def hub_search_query(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    query = (message.text or "").strip()
    if not query:
        await message.answer(t(lang, "search_enter"))
        return
    records = await unified_search(session, user.id, query)
    lines = format_unified_search(records, lang, query)
    if records.has_any():
        context = build_search_ai_context(records)
        loading = await message.answer(t(lang, "ai_thinking"))
        hint = t(lang, "eco_search_ai_hint")
        answer = await ask_ai(
            user_message=query,
            module_hint=hint,
            memory_context=context,
            language=lang,
        )
        lines.append(f"\n🤖 <b>{t(lang, 'eco_search_ai_title')}</b>\n{answer}")
        await loading.delete()
    await message.answer("\n".join(lines), reply_markup=back_menu_kb(lang))
    await state.clear()


@router.callback_query(F.data == "hub:settings")
async def hub_settings(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    mem = "✅" if user.memory_enabled else "❌"
    voice = "✅" if user.voice_mode else "❌"
    await callback.message.edit_text(
        f"{t(lang, 'settings_title')}\n\n"
        f"{t(lang, 'settings_memory', status=mem)}\n"
        f"{t(lang, 'settings_voice', status=voice)}\n"
        f"{t(lang, 'settings_lang', label=LANG_LABELS.get(lang, lang.upper()))}\n\n"
        f"{t(lang, 'settings_tip')}\n\n"
        f"{t(lang, 'settings_extra')}",
        reply_markup=settings_kb(user.memory_enabled, user.voice_mode, lang),
    )
    await callback.answer()


@router.callback_query(F.data == "hub:help")
async def hub_help(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    await callback.message.edit_text(t(lang, "help_text"), reply_markup=help_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "hub:language")
async def hub_language(callback: CallbackQuery, user: User) -> None:
    lang = _lang(user)
    await callback.message.edit_text(t(lang, "choose_language"), reply_markup=language_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("set:lang:"))
async def settings_set_language(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    code = (callback.data or "").split(":")[2]
    new_lang = await set_user_language(session, user, code)
    await callback.message.edit_text(
        t(new_lang, "language_changed", label=LANG_LABELS[new_lang]),
        reply_markup=dashboard_kb(new_lang),
    )
    await callback.answer()


@router.callback_query(F.data == "set:memory")
async def settings_toggle_memory(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    enabled = await toggle_memory(session, user)
    await callback.message.edit_reply_markup(reply_markup=settings_kb(enabled, user.voice_mode, lang))
    await callback.answer(t(lang, "memory_on_toast") if enabled else t(lang, "memory_off_toast"))


@router.callback_query(F.data == "set:voice")
async def settings_toggle_voice(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = _lang(user)
    enabled = await toggle_voice_mode(session, user)
    await callback.answer(t(lang, "voice_on_toast") if enabled else t(lang, "voice_off_toast"))
    if callback.message and callback.message.text:
        await callback.message.edit_reply_markup(reply_markup=settings_kb(user.memory_enabled, enabled, lang))
