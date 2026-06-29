from __future__ import annotations

import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ai_reply_ui import deliver_ai_reply
from app.bot.keyboards import back_menu_kb, dashboard_kb, record_saved_kb
from app.bot.keyboards_subscription import insufficient_credits_kb
from app.bot.message_ui import deliver_long_text
from app.bot.states import ScanStates
from app.core.i18n import ai_reply_language, t
from app.models.entities import User
from app.services.ai_context import build_ai_memory_context
from app.services.ai_service import ask_ai
from app.services.intent_router import check_url_security, module_hint
from app.services.life_data import add_memory, add_record
from app.services.life_profile_service import parse_remember_text
from app.services.media_ai import analyze_image_url, get_telegram_image_url, synthesize_speech, transcribe_voice
from app.services.module_context import active_module_label
from app.services.proactive_service import proactive_kb, suggest_actions
from app.services.scanner_service import archive_label, archive_meta, classify_scan, parse_amount_from_text, universal_scan_prompt
from app.services.subscription_service import parse_insufficient_credits_reply
from app.services.vault_service import (
    VAULT_FILE_SUBMODULES,
    vault_file_meta,
    vault_file_title,
    vault_folder_for_submodule,
    vault_search_tags,
)
from app.bot.states import VaultStates

router = Router()


def _vision_prompt(
    lang: str,
    caption: str = "",
    *,
    car_dashboard: bool = False,
    legal_document: bool = False,
    assistant_photo: bool = False,
    universal: bool = False,
) -> str:
    if universal:
        return universal_scan_prompt(lang, caption)
    reply_lang = ai_reply_language(lang)
    if assistant_photo:
        prompt = (
            "Analyze this photo in detail: objects, people, text (OCR), documents, receipts, "
            f"scenes, colors, context. Reply in {reply_lang}."
        )
    elif car_dashboard:
        prompt = (
            "Car dashboard photo. Warning lights, error codes, urgency, safe to drive. "
            f"Reply in {reply_lang}."
        )
    elif legal_document:
        prompt = f"Legal document photo. Key terms and risks. Reply in {reply_lang}."
    else:
        prompt = f"Analyze image: receipt, document, or car error. Reply in {reply_lang}."
    if caption:
        prompt += f"\nUser caption: {caption}"
    return prompt


async def _process_photo(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext | None = None,
    *,
    universal_scan: bool = False,
) -> None:
    lang = user.language
    from app.core.credits import photo_analysis_credits
    from app.services.model_router import select_vision_model
    from app.services.subscription_service import (
        check_photo_analysis_quota,
        consume_photo_analysis,
        feature_allowed,
    )

    if (
        not universal_scan
        and user.active_module_id == "vault"
        and user.active_submodule_id in VAULT_FILE_SUBMODULES
    ):
        if state is None:
            await message.answer(t(lang, "vlt_use_add_flow"))
            return
        current = await state.get_state()
        if current == VaultStates.waiting_attachment.state:
            return
        await message.answer(t(lang, "vlt_use_add_flow"))
        return
    if not universal_scan:
        blocked = feature_allowed(user, "photo_ai")
        if blocked:
            await message.answer(t(lang, blocked))
            return
        photo_credits = photo_analysis_credits(multi=False)
        photo_quota = await check_photo_analysis_quota(session, user, lang=lang, credits=photo_credits)
        if photo_quota:
            await message.answer(photo_quota)
            return
    file_id = message.photo[-1].file_id
    caption = (message.caption or "").strip()
    loading = await message.answer(t(lang, "photo_analyzing"))
    image_url = await get_telegram_image_url(bot, file_id)
    car_mode = user.active_module_id == "car" and user.active_submodule_id in (None, "panel_photo")
    legal_mode = user.active_module_id == "legal" and user.active_submodule_id == "doc_check"
    assistant_photo = user.active_module_id == "ai_assistant" and user.active_submodule_id == "photo"
    vision_model = select_vision_model(
        user,
        module_id=user.active_module_id,
        caption=caption,
        legal_document=legal_mode and not universal_scan,
        car_dashboard=car_mode and not universal_scan,
    )
    analysis = await analyze_image_url(
        image_url,
        _vision_prompt(
            lang,
            caption,
            car_dashboard=car_mode and not universal_scan,
            legal_document=legal_mode and not universal_scan,
            assistant_photo=assistant_photo and not universal_scan,
            universal=universal_scan,
        ),
        model=vision_model,
        session=session,
        user_id=user.id,
        user=user,
        bot=message.bot,
    )
    if not universal_scan:
        await consume_photo_analysis(session, user, credits=photo_credits)
    lowered = analysis.lower()
    combined = f"{caption} {analysis}".lower()

    if universal_scan:
        module_id, sub_id, folder = classify_scan(analysis, caption)
    else:
        module_id, sub_id, folder = "vault", "receipts", "receipts"
        if user.active_module_id == "vault" and user.active_submodule_id in VAULT_FILE_SUBMODULES:
            module_id, sub_id = "vault", user.active_submodule_id
            folder = vault_folder_for_submodule(user.active_submodule_id)
        elif user.active_module_id == "legal" and user.active_submodule_id == "doc_check":
            module_id, sub_id, folder = "legal", "doc_check", "contracts"
        elif assistant_photo:
            module_id, sub_id, folder = "ai_assistant", "photo", "photos"
        elif car_mode or any(x in lowered for x in ("ошибк", "error", "obd", "dashboard", "check engine")):
            module_id, sub_id, folder = "car", "panel_photo", "car"
        elif any(x in lowered for x in ("паспорт", "passport", "договор", "contract", "полис")):
            module_id, sub_id, folder = "vault", "documents", "passport"
        elif user.active_module_id == "health" or any(
            x in combined for x in ("анализ", "tahlil", "analysis", "blood", "medical", "lab")
        ):
            module_id, sub_id, folder = "health", "documents", "analyses"

    amount = parse_amount_from_text(analysis)
    extra = ""
    if any(x in combined for x in ("холодильник", "fridge", "recipe", "retsept", "ovqat")):
        profile_ctx, memory_ctx = await build_ai_memory_context(session, user, caption or "food")
        recipes = await ask_ai(
            user_message=f"Suggest 2-3 recipes from visible products:\n{analysis[:800]}",
            module_hint=module_hint("nutrition", "recipes", lang=lang),
            memory_context=memory_ctx,
            profile_context=profile_ctx,
            language=lang,
            session=session,
            user=user,
            bot=message.bot,
        )
        is_quota, recipe_body = parse_insufficient_credits_reply(recipes)
        extra = f"\n\n{recipe_body}" if is_quota else f"\n\n🍽 {recipe_body}"

    search_prefix = f"{vault_search_tags(sub_id)}\n" if module_id == "vault" else ""
    title = caption[:200] or (
        vault_file_title(sub_id, lang) if module_id == "vault" else t(lang, "photo_title_default")
    )
    meta_json = (
        vault_file_meta(sub_id, file_id, folder=folder)
        if module_id == "vault"
        else archive_meta(folder, scan=universal_scan)
    )
    await add_record(
        session,
        user_id=user.id,
        module_id=module_id,
        submodule_id=sub_id,
        title=title,
        body=f"{search_prefix}file_id={file_id}\n\n{analysis}",
        amount=amount,
        currency="UZS" if amount else None,
        profile_id=user.active_profile_id,
        meta_json=meta_json,
    )
    folder_label = archive_label(folder, lang)
    text = f"{t(lang, 'scan_saved', folder=folder_label) if universal_scan else t(lang, 'photo_done')}\n{folder_label}\n\n{analysis}{extra}"
    if amount:
        text += f"\n\n💰 {amount:,.0f} UZS"
    kb = record_saved_kb(lang)
    if universal_scan:
        from app.bot.keyboards_ecosystem import scan_followup_kb

        if state is not None and amount:
            await state.update_data(scan_amount=amount)
        kb = scan_followup_kb(lang, amount=amount)
    await deliver_long_text(loading, text, reply_markup=kb)


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot, user: User, session: AsyncSession) -> None:
    lang = user.language
    from app.services.subscription_service import feature_allowed

    blocked = feature_allowed(user, "voice")
    if blocked:
        await message.answer(t(lang, blocked))
        return
    loading = await message.answer(t(lang, "voice_recognizing"))
    text = await transcribe_voice(bot, message.voice.file_id)
    if not text:
        await loading.edit_text(t(lang, "voice_failed"))
        return
    await loading.edit_text(f"🎤 <i>{text}</i>")
    remember = parse_remember_text(text)
    if remember:
        await add_memory(session, user.id, remember, module_id="profile", profile_id=user.active_profile_id)
        await message.answer(t(lang, "remember_saved", text=remember[:200]), reply_markup=dashboard_kb(lang))
        return
    hint = module_hint(user.active_module_id, user.active_submodule_id, lang=lang) if user.active_module_id else ""
    profile_ctx, memory_ctx = await build_ai_memory_context(session, user, text)
    answer = await ask_ai(
        user_message=text,
        module_hint=hint,
        memory_context=memory_ctx,
        profile_context=profile_ctx,
        language=lang,
        session=session,
        user=user,
        bot=message.bot,
    )
    header = active_module_label(user.active_module_id, user.active_submodule_id, lang=lang)
    actions = suggest_actions(text, answer, lang)
    kb = proactive_kb(actions, lang) or dashboard_kb(lang)
    is_quota = await deliver_ai_reply(
        message,
        answer,
        lang=lang,
        prefix=f"{header}\n\n" if header else "🤖 ",
        reply_markup=kb,
    )
    if not is_quota and user.memory_enabled:
        await add_memory(
            session,
            user.id,
            f"[voice] Q: {text[:200]}\nA: {answer[:400]}",
            module_id=user.active_module_id or "ai_assistant",
            profile_id=user.active_profile_id,
        )


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, user: User, session: AsyncSession, state: FSMContext) -> None:
    current = await state.get_state()
    universal = current == ScanStates.waiting_photo.state
    await _process_photo(message, bot, user, session, state, universal_scan=universal)
    if universal:
        await state.clear()


@router.message(F.document)
async def handle_document(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    lang = user.language
    vault_docs = user.active_module_id == "vault" and user.active_submodule_id in VAULT_FILE_SUBMODULES
    if vault_docs:
        current = await state.get_state()
        if current == VaultStates.waiting_attachment.state:
            return
        await message.answer(t(lang, "vlt_use_add_flow"))
        return
    doc = message.document
    name = doc.file_name or "document"
    assistant_docs = user.active_module_id == "ai_assistant" and user.active_submodule_id == "documents"
    if vault_docs:
        module_id, sub_id = "vault", user.active_submodule_id
    elif assistant_docs:
        module_id, sub_id = "ai_assistant", "documents"
    else:
        module_id, sub_id = "vault", "documents"
    folder = vault_folder_for_submodule(sub_id) if module_id == "vault" else "contracts"
    search_prefix = f"{vault_search_tags(sub_id)}\n" if module_id == "vault" else ""
    title = name[:200]
    if module_id == "vault" and name in ("document", "file"):
        title = vault_file_title(sub_id, lang)
    meta_json = (
        vault_file_meta(sub_id, doc.file_id, mime=doc.mime_type, folder=folder, kind="document")
        if module_id == "vault"
        else archive_meta(folder)
    )
    await add_record(
        session,
        user_id=user.id,
        module_id=module_id,
        submodule_id=sub_id,
        title=title,
        body=f"{search_prefix}file_id={doc.file_id}\nmime={doc.mime_type}",
        profile_id=user.active_profile_id,
        meta_json=meta_json,
    )
    if assistant_docs:
        await message.answer(t(lang, "ast_doc_saved", name=name), reply_markup=back_menu_kb(lang))
        return
    await message.answer(t(lang, "doc_saved", name=name), reply_markup=record_saved_kb(lang))


@router.message(F.text.regexp(r"https?://\S+"))
async def handle_link(message: Message, user: User, session: AsyncSession) -> None:
    lang = user.language
    match = re.search(r"https?://\S+", message.text or "")
    if not match:
        return
    url = match.group(0).rstrip(").,")
    check = check_url_security(url)
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(check["risk"], "⚪")
    profile_ctx, memory_ctx = await build_ai_memory_context(session, user, url)
    ai = await ask_ai(
        user_message=f"Check link for fraud: {url}\nHeuristic: {check['summary']}",
        module_hint=module_hint("ai_assistant", lang=lang),
        memory_context=memory_ctx,
        profile_context=profile_ctx,
        language=lang,
        session=session,
        user=user,
        bot=message.bot,
    )
    is_quota, body = parse_insufficient_credits_reply(ai)
    if is_quota:
        await message.answer(body, reply_markup=insufficient_credits_kb(lang))
        return
    await message.answer(
        f"{t(lang, 'link_check')}\n\n{risk_emoji} {t(lang, 'link_risk', risk=check['risk'])}\n{check['summary']}\n\n🤖 {body}",
        reply_markup=back_menu_kb(lang),
    )
