from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import family_kb, family_relation_kb
from app.bot.states import FamilyStates
from app.core.i18n import t
from app.models.entities import User
from app.services.life_data import add_family_profile, list_family_profiles, switch_active_profile
from app.services.subscription_service import check_family_profile_quota

router = Router()


@router.callback_query(F.data == "hub:family")
async def family_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    profiles = await list_family_profiles(session, user.id)
    active = next((p for p in profiles if p.id == user.active_profile_id), profiles[0] if profiles else None)
    lines = [t(lang, "family_title"), t(lang, "family_desc"), ""]
    for p in profiles:
        mark = "✅ " if p.id == user.active_profile_id else "• "
        lines.append(f"{mark}<b>{p.name}</b> ({p.relation})")
    if active:
        lines.append(f"\n{t(lang, 'family_active', name=active.name)}")
    await callback.message.edit_text("\n".join(lines), reply_markup=family_kb(profiles, user.active_profile_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("fam:switch:"))
async def family_switch(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    profile_id = int((callback.data or "").split(":")[2])
    ok = await switch_active_profile(session, user, profile_id)
    if not ok:
        await callback.answer(t(lang, "family_not_found"), show_alert=True)
        return
    profiles = await list_family_profiles(session, user.id)
    await callback.message.edit_reply_markup(reply_markup=family_kb(profiles, profile_id, lang))
    await callback.answer(t(lang, "family_switched"))


@router.callback_query(F.data == "fam:add")
async def family_add_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.set_state(FamilyStates.waiting_name)
    await callback.message.answer(t(user.language, "family_add_name"))
    await callback.answer()


@router.message(FamilyStates.waiting_name)
async def family_add_name(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(t(lang, "family_name_short"))
        return
    await state.update_data(fam_name=name)
    quota = await check_family_profile_quota(session, user, lang=lang)
    if quota:
        from app.bot.quota_ui import answer_quota_block

        await answer_quota_block(message, quota, lang=lang)
        await state.clear()
        return
    await state.set_state(FamilyStates.waiting_relation)
    await message.answer(t(lang, "family_add_relation"), reply_markup=family_relation_kb(lang))


@router.callback_query(F.data.startswith("fam:rel:"))
async def family_add_relation_pick(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    relation = (callback.data or "").split(":")[2]
    data = await state.get_data()
    name = str(data.get("fam_name") or "Profile")
    quota = await check_family_profile_quota(session, user, lang=lang)
    if quota:
        from app.bot.quota_ui import answer_quota_block

        await answer_quota_block(callback.message, quota, lang=lang)
        await state.clear()
        await callback.answer()
        return
    await add_family_profile(session, user.id, name, relation)
    profiles = await list_family_profiles(session, user.id)
    await callback.message.edit_text(t(lang, "family_added", name=name), reply_markup=family_kb(profiles, user.active_profile_id, lang))
    await state.clear()
    await callback.answer()


@router.message(FamilyStates.waiting_relation)
async def family_add_relation(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    lang = user.language
    relation = (message.text or "other").strip()[:64]
    data = await state.get_data()
    name = str(data.get("fam_name") or "Profile")
    quota = await check_family_profile_quota(session, user, lang=lang)
    if quota:
        from app.bot.quota_ui import answer_quota_block

        await answer_quota_block(message, quota, lang=lang)
        await state.clear()
        return
    await add_family_profile(session, user.id, name, relation)
    profiles = await list_family_profiles(session, user.id)
    await message.answer(t(lang, "family_added", name=name), reply_markup=family_kb(profiles, user.active_profile_id, lang))
    await state.clear()
