from __future__ import annotations



from aiogram import F, Router

from aiogram.types import CallbackQuery, Message

from sqlalchemy.ext.asyncio import AsyncSession



from app.bot.keyboards_assistant import assistant_ai_kb, assistant_module_kb
from app.bot.message_ui import edit_or_answer_text
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import User
from app.services.assistant_service import assistant_submodule_description
from app.services.life_data import set_active_module
from app.core.credits import image_generation_credits
from app.services.media_ai import generate_image
from app.services.subscription_service import (
    check_image_gen_quota,
    consume_image_generation,
    feature_allowed,
    image_quality_for_user,
)

router = Router()
text_router = Router()


async def reply_with_generated_image(message: Message, user: User, session: AsyncSession, prompt: str) -> None:
    lang = user.language
    kb = assistant_ai_kb("ai_assistant", "images", lang)
    text = prompt.strip()
    if len(text) < 2:
        await message.answer(t(lang, "ast_send_image_prompt"), reply_markup=kb)
        return
    blocked = feature_allowed(user, "image_gen")
    if blocked:
        await message.answer(t(lang, blocked))
        return
    quality = image_quality_for_user(user)
    img_credits = image_generation_credits(quality)  # type: ignore[arg-type]
    quota_msg = await check_image_gen_quota(session, user, lang=lang, credits=img_credits)
    if quota_msg:
        await message.answer(quota_msg)
        return
    wait_msg = await message.answer(t(lang, "ast_image_generating"))
    try:
        result = await generate_image(text, quality=quality)
    except Exception:
        result = None
    if not result:
        await wait_msg.edit_text(t(lang, "ast_image_failed"), reply_markup=kb)
        return
    image_bytes, model_used, api_response = result
    await consume_image_generation(session, user, credits=img_credits)
    from app.services.ai_usage_service import record_image_usage

    await record_image_usage(
        session,
        user.id,
        model_used,
        quality=quality,
        response=api_response,
    )
    from aiogram.types import BufferedInputFile

    await message.answer_photo(
        BufferedInputFile(image_bytes, filename="generated.png"),
        caption=t(lang, "ast_image_done", prompt=text[:200]),
        reply_markup=kb,
    )


@router.callback_query(F.data == "mod:ai_assistant")
async def assistant_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    await set_active_module(session, user, "ai_assistant")
    await edit_or_answer_text(
        callback.message,
        t(lang, "ast_module_intro"),
        reply_markup=assistant_module_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sub:ai_assistant:"))
async def assistant_submodule(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["ai_assistant"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "ai_assistant", submodule_id=sub_id)
    desc = assistant_submodule_description(sub_id, lang)
    extra = ""
    if sub_id == "photo":
        extra = f"\n\n{t(lang, 'ast_send_photo')}"
    elif sub_id == "documents":
        extra = f"\n\n{t(lang, 'ast_send_document')}"
    elif sub_id == "images":
        extra = f"\n\n{t(lang, 'ast_send_image_prompt')}"
    text = (
        f"🤖 <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n"
        f"{desc}{extra}\n\n{t(lang, 'ast_ai_hint')}"
    )
    await edit_or_answer_text(
        callback.message,
        text,
        reply_markup=assistant_ai_kb("ai_assistant", sub_id, lang),
    )
    await callback.answer()

