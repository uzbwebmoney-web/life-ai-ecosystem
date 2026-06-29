from __future__ import annotations



from aiogram import Bot, F, Router

from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery, Message

from sqlalchemy.ext.asyncio import AsyncSession



from app.bot.message_ui import safe_callback_answer, safe_edit_text

from app.bot.keyboards_education import (

    education_ai_kb,

    education_module_kb,

    study_followup_kb,

    study_spec_kb,

)

from app.bot.states import EducationStates

from app.core.i18n import t

from app.core.modules.catalog import MODULE_BY_ID

from app.models.entities import User

from app.services.education_service import education_submodule_description

from app.services.life_data import set_active_module

from app.services.study_notes_service import combine_study_request, study_spec_from_callback



router = Router()





@router.callback_query(F.data == "mod:education")

async def education_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:

    lang = user.language

    await safe_callback_answer(callback)

    await set_active_module(session, user, "education")

    await safe_edit_text(callback.message, t(lang, "edu_module_intro"), reply_markup=education_module_kb(lang))





@router.callback_query(F.data.startswith("sub:education:"))

async def education_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:

    lang = user.language

    sub_id = (callback.data or "").split(":")[2]

    mod = MODULE_BY_ID["education"]

    sub = next((s for s in mod.submodules if s.id == sub_id), None)

    if not sub:

        await callback.answer(t(lang, "not_found"), show_alert=True)

        return

    await safe_callback_answer(callback)

    await set_active_module(session, user, "education", submodule_id=sub_id)

    desc = education_submodule_description(sub_id, lang)

    text = (

        f"📚 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"

        f"{desc}\n\n{t(lang, 'edu_ai_hint')}"

    )

    await safe_edit_text(callback.message, text, reply_markup=education_ai_kb("education", sub_id, lang))





@router.callback_query(F.data == "edu:spec:cancel")

async def education_spec_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:

    lang = user.language

    await state.clear()

    await safe_callback_answer(callback)

    await safe_edit_text(callback.message, t(lang, "btn_cancel"), reply_markup=education_module_kb(lang))





@router.callback_query(F.data.startswith("edu:spec:"))

async def education_spec_pick(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession, bot: Bot) -> None:

    parts = (callback.data or "").split(":")

    if len(parts) < 4:

        await callback.answer()

        return

    try:

        pages = int(parts[2])

        fmt = parts[3]

    except (ValueError, IndexError):

        await callback.answer()

        return

    lang = user.language

    data = await state.get_data()

    topic = str(data.get("study_topic") or "")

    module_id = str(data.get("study_module_id") or "education")

    submodule_id = data.get("study_submodule_id")

    spec = study_spec_from_callback(pages, fmt)

    combined = combine_study_request(topic, spec)

    await state.clear()

    await callback.answer()

    from app.bot.handlers.free_text import answer_in_module



    await answer_in_module(

        callback.message,

        bot=bot,

        user=user,

        session=session,

        state=state,

        text=combined,

        module_id=module_id,

        submodule_id=submodule_id,

    )





@router.callback_query(F.data.startswith("edu:exp:"))

async def education_export_pick(callback: CallbackQuery, user: User, session: AsyncSession) -> None:

    fmt = (callback.data or "").split(":")[-1]

    if fmt not in {"pdf", "docx", "txt", "md"}:

        await callback.answer()

        return

    lang = user.language

    await callback.answer()

    await export_last_study_document(callback.message, user, session, fmt=fmt)  # type: ignore[arg-type]





@router.message(EducationStates.waiting_study_spec, F.text)

async def education_study_spec_text(

    message: Message,

    bot: Bot,

    user: User,

    session: AsyncSession,

    state: FSMContext,

) -> None:

    spec = (message.text or "").strip()

    if not spec:

        return

    data = await state.get_data()

    topic = str(data.get("study_topic") or "")

    module_id = str(data.get("study_module_id") or "education")

    submodule_id = data.get("study_submodule_id")

    combined = combine_study_request(topic, spec)

    await state.clear()

    from app.bot.handlers.free_text import answer_in_module



    await answer_in_module(

        message,

        bot=bot,

        user=user,

        session=session,

        state=state,

        text=combined,

        module_id=module_id,

        submodule_id=submodule_id,

    )


