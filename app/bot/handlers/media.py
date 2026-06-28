from __future__ import annotations

import re

from aiogram import Bot, F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb
from app.core.i18n import ai_reply_language, t
from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.intent_router import check_url_security, module_hint
from app.services.life_data import add_memory, add_record, search_memory
from app.services.module_context import active_module_label
from app.services.media_ai import analyze_image_url, get_telegram_image_url, transcribe_voice
from app.services.vault_service import VAULT_FILE_SUBMODULES

router = Router()


def _vision_prompt(lang: str, caption: str = "", *, car_dashboard: bool = False, legal_document: bool = False, assistant_photo: bool = False) -> str:
    reply_lang = ai_reply_language(lang)
    if assistant_photo:
        prompt = (
            "Analyze this photo in detail: objects, people, text (OCR), documents, receipts, "
            "scenes, colors, context. Answer the user's question if provided. "
            f"Reply in {reply_lang}."
        )
    elif car_dashboard:
        prompt = (
            "This is a car instrument panel / dashboard photo. Identify warning lights, error codes, "
            "gauges. Explain meaning, urgency, whether safe to drive, recommended checks. "
            f"Reply in {reply_lang}."
        )
    elif legal_document:
        prompt = (
            "This is a legal document photo. Identify document type, parties, dates, key terms, "
            "potential risks, missing clauses, inconsistencies. Do not give definitive legal advice — "
            "note what should be verified with a lawyer. "
            f"Reply in {reply_lang}."
        )
    else:
        prompt = (
            "Analyze the image. If receipt — store, date, amount, currency, items. "
            "If document — type, key fields, dates. If car error — code and description. "
            f"Reply in {reply_lang}."
        )
    if caption:
        prompt += f"\nUser caption: {caption}"
    return prompt


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot, user: User, session: AsyncSession) -> None:
    lang = user.language
    loading = await message.answer(t(lang, "voice_recognizing"))
    text = await transcribe_voice(bot, message.voice.file_id)
    if not text:
        await loading.edit_text(t(lang, "voice_failed"))
        return
    await loading.edit_text(f"🎤 <i>{text}</i>")
    hint = module_hint(user.active_module_id, user.active_submodule_id, lang=lang) if user.active_module_id else ""
    memory_ctx = ""
    if user.memory_enabled:
        entries = await search_memory(session, user.id, text, limit=3)
        if entries:
            memory_ctx = "\n".join(e.content for e in entries)
    if user.voice_mode:
        await message.answer(t(lang, "eco_voice_mode_hint"))
    answer = await ask_ai(user_message=text, module_hint=hint, memory_context=memory_ctx, language=lang)
    header = active_module_label(user.active_module_id, user.active_submodule_id, lang=lang)
    prefix = f"{header}\n\n" if header else "🤖 "
    await message.answer(f"{prefix}{answer}")
    if user.memory_enabled:
        await add_memory(
            session,
            user.id,
            f"[voice] Q: {text[:200]}\nA: {answer[:400]}",
            module_id=user.active_module_id or "ai_assistant",
            profile_id=user.active_profile_id,
        )


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, user: User, session: AsyncSession) -> None:
    lang = user.language
    file_id = message.photo[-1].file_id
    caption = (message.caption or "").strip()
    loading = await message.answer(t(lang, "photo_analyzing"))
    image_url = await get_telegram_image_url(bot, file_id)
    car_mode = user.active_module_id == "car" and user.active_submodule_id in (None, "panel_photo")
    legal_mode = user.active_module_id == "legal" and user.active_submodule_id == "doc_check"
    assistant_photo = user.active_module_id == "ai_assistant" and user.active_submodule_id == "photo"
    analysis = await analyze_image_url(
        image_url,
        _vision_prompt(
            lang,
            caption,
            car_dashboard=car_mode,
            legal_document=legal_mode,
            assistant_photo=assistant_photo,
        ),
    )
    lowered = analysis.lower()
    combined = f"{caption} {analysis}".lower()
    module_id = "vault"
    sub_id = "receipts"
    vault_mode = user.active_module_id == "vault"
    if vault_mode and user.active_submodule_id in VAULT_FILE_SUBMODULES:
        module_id, sub_id = "vault", user.active_submodule_id
    if legal_mode:
        module_id, sub_id = "legal", "doc_check"
    elif assistant_photo:
        module_id, sub_id = "ai_assistant", "photo"
    elif car_mode or any(x in lowered for x in ("ошибк", "error", "obd", "двигател", "xato", "check engine", "dashboard")):
        module_id, sub_id = "car", "panel_photo"
    elif any(x in lowered for x in ("паспорт", "договор", "полис", "passport", "contract")):
        module_id, sub_id = "vault", "documents"
    elif user.active_module_id == "health" or any(
        x in combined for x in ("анализ", "tahlil", "analysis", "blood", "qon", "справк", "medical", "lab")
    ):
        module_id, sub_id = "health", "documents"
    await add_record(
        session,
        user_id=user.id,
        module_id=module_id,
        submodule_id=sub_id,
        title=caption[:200] or t(lang, "photo_title_default"),
        body=f"file_id={file_id}\n\n{analysis}",
        profile_id=user.active_profile_id,
    )
    await loading.edit_text(f"{t(lang, 'photo_done')}\n\n{analysis}", reply_markup=back_menu_kb(lang))


@router.message(F.document)
async def handle_document(message: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    doc = message.document
    name = doc.file_name or "document"
    assistant_docs = user.active_module_id == "ai_assistant" and user.active_submodule_id == "documents"
    vault_docs = user.active_module_id == "vault" and user.active_submodule_id in VAULT_FILE_SUBMODULES
    if vault_docs:
        module_id, sub_id = "vault", user.active_submodule_id
    elif assistant_docs:
        module_id, sub_id = "ai_assistant", "documents"
    else:
        module_id, sub_id = "vault", "documents"
    await add_record(
        session,
        user_id=user.id,
        module_id=module_id,
        submodule_id=sub_id,
        title=name[:200],
        body=f"file_id={doc.file_id}\nmime={doc.mime_type}",
        profile_id=user.active_profile_id,
    )
    if assistant_docs:
        caption = (message.caption or "").strip()
        hint = t(lang, "ast_doc_saved", name=name)
        if caption:
            hint = f"{hint}\n\n{t(lang, 'ast_doc_caption_note')}"
        await message.answer(hint, reply_markup=back_menu_kb(lang))
        return
    await message.answer(t(lang, "doc_saved", name=name), reply_markup=back_menu_kb(lang))


@router.message(F.text.regexp(r"https?://\S+"))
async def handle_link(message: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    match = re.search(r"https?://\S+", message.text or "")
    if not match:
        return
    url = match.group(0).rstrip(").,")
    check = check_url_security(url)
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(check["risk"], "⚪")
    ai = await ask_ai(
        user_message=f"Check link for fraud: {url}\nHeuristic: {check['summary']}",
        module_hint=module_hint("ai_assistant", lang=lang),
        language=lang,
    )
    await message.answer(
        f"{t(lang, 'link_check')}\n\n{risk_emoji} {t(lang, 'link_risk', risk=check['risk'])}\n{check['summary']}\n\n🤖 {ai}",
        reply_markup=back_menu_kb(lang),
    )
