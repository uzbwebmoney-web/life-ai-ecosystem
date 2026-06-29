from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards_music import music_after_lyrics_kb, music_cancel_kb, music_module_kb, music_sub_kb
from app.bot.message_ui import deliver_long_text
from app.bot.states import MusicStates
from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import LifeRecord, User
from app.services.ai_service import ask_ai
from app.services.life_data import add_record, set_active_module
from app.services.module_context import build_module_ai_hint
from app.services.music_service import (
    audio_from_message,
    build_analyze_prompt,
    build_chords_prompt,
    build_translate_prompt,
    download_audio_bytes,
    music_submodule_description,
    separate_audio,
    transcribe_song_lyrics,
)
from app.services.subscription_service import (
    check_music_quota,
    consume_music_operation,
    parse_insufficient_credits_reply,
)

logger = logging.getLogger(__name__)

router = Router()


async def _music_quota_blocked(
    message: Message,
    user: User,
    session: AsyncSession,
    *,
    separate: bool = False,
) -> bool:
    blocked = await check_music_quota(session, user, lang=user.language, separate=separate)
    if blocked:
        from app.bot.quota_ui import answer_quota_block

        await answer_quota_block(message, blocked, lang=user.language)
        return True
    return False


@router.callback_query(F.data == "mod:music")
async def music_module(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    from app.services.subscription_service import check_module_access

    blocked = await check_module_access(session, user, "music", lang=lang)
    if blocked:
        from app.bot.quota_ui import answer_quota_block

        await answer_quota_block(callback.message, blocked, lang=lang)
        await callback.answer()
        return
    await set_active_module(session, user, "music")
    mod = MODULE_BY_ID["music"]
    text = f"{mod.emoji} <b>{mod.title(lang)}</b>\n\n{t(lang, 'mus_module_intro')}"
    await callback.message.edit_text(text, reply_markup=music_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:music:"))
async def music_submodule(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    lang = user.language
    sub_id = (callback.data or "").split(":")[2]
    mod = MODULE_BY_ID["music"]
    sub = next((s for s in mod.submodules if s.id == sub_id), None)
    if not sub:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await set_active_module(session, user, "music", submodule_id=sub_id)
    await state.clear()
    desc = music_submodule_description(sub_id, lang)
    text = f"{mod.emoji} <b>{mod.title(lang)}</b> → <b>{sub.title(lang)}</b>\n\n{desc}\n\n{t(lang, 'mus_upload_hint')}"
    await callback.message.edit_text(text, reply_markup=music_sub_kb(sub_id, lang))
    await callback.answer()


@router.callback_query(F.data == "mus:cancel")
async def music_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    lang = user.language
    await callback.message.edit_text(t(lang, "mus_cancelled"), reply_markup=music_module_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "mus:mode:lyrics")
async def music_mode_lyrics(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(MusicStates.waiting_audio)
    await state.update_data(mus_action="lyrics", mus_mode="lyrics")
    await callback.message.answer(t(lang, "mus_send_audio"), reply_markup=music_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("mus:mode:"))
async def music_mode_separate(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    mode = (callback.data or "").split(":")[-1]
    if mode == "lyrics":
        return
    lang = user.language
    await state.set_state(MusicStates.waiting_audio)
    await state.update_data(mus_action="separate", mus_mode=mode)
    await callback.message.answer(t(lang, "mus_send_audio"), reply_markup=music_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("mus:from_audio:"))
async def music_from_audio(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    action = (callback.data or "").split(":")[-1]
    lang = user.language
    await state.set_state(MusicStates.waiting_audio)
    await state.update_data(mus_action=action, mus_mode="audio")
    await callback.message.answer(t(lang, "mus_send_audio"), reply_markup=music_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("mus:paste:"))
async def music_paste_text(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    action = (callback.data or "").split(":")[-1]
    lang = user.language
    await state.set_state(MusicStates.waiting_lyrics_text)
    await state.update_data(mus_action=action)
    await callback.message.answer(t(lang, "mus_paste_lyrics"), reply_markup=music_cancel_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("mus:quick:"))
async def music_quick_action(
    callback: CallbackQuery,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    action = (callback.data or "").split(":")[-1]
    data = await state.get_data()
    lyrics = (data.get("last_lyrics") or "").strip()
    lang = user.language
    if not lyrics:
        await callback.answer(t(lang, "mus_no_lyrics"), show_alert=True)
        return
    await callback.answer()
    if await _music_quota_blocked(callback.message, user, session):
        return
    await _run_text_action(callback.message, bot, user, session, action, lyrics, lang)


@router.callback_query(F.data == "mus:collection:view")
async def music_collection_view(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    lang = user.language
    result = await session.execute(
        select(LifeRecord)
        .where(LifeRecord.user_id == user.id, LifeRecord.module_id == "music", LifeRecord.submodule_id == "collection")
        .order_by(LifeRecord.id.desc())
        .limit(15)
    )
    rows = list(result.scalars())
    lines = [t(lang, "mus_collection_title"), ""]
    if rows:
        for row in rows:
            lines.append(f"• <b>{row.title}</b>\n{row.body[:300]}")
    else:
        lines.append(t(lang, "mus_collection_empty"))
    await callback.message.edit_text("\n\n".join(lines), reply_markup=music_sub_kb("collection", lang))
    await callback.answer()


@router.callback_query(F.data == "mus:collection:save")
async def music_collection_save(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    lang = user.language
    data = await state.get_data()
    lyrics = (data.get("last_lyrics") or "").strip()
    title = (data.get("last_title") or t(lang, "mus_untitled")).strip()[:200]
    if not lyrics:
        await callback.answer(t(lang, "mus_no_lyrics"), show_alert=True)
        return
    await add_record(
        session,
        user_id=user.id,
        module_id="music",
        submodule_id="collection",
        title=title,
        body=lyrics[:4000],
        profile_id=user.active_profile_id,
    )
    await callback.answer(t(lang, "mus_saved_collection"), show_alert=True)


async def _run_text_action(
    target: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    action: str,
    lyrics: str,
    lang: str,
    *,
    consume: bool = True,
) -> None:
    if action == "analyze":
        prompt = build_analyze_prompt(lyrics, lang)
    elif action == "translate":
        prompt = build_translate_prompt(lyrics, lang)
    elif action == "chords":
        prompt = build_chords_prompt(lyrics, lang)
    else:
        return

    loading = await target.answer(t(lang, "mus_processing"))
    hint = build_module_ai_hint("music", action, lang=lang)
    answer = await ask_ai(
        user_message=prompt,
        module_hint=hint,
        language=lang,
        session=session,
        user=user,
        bot=bot,
    )
    is_quota, body = parse_insufficient_credits_reply(answer)
    if is_quota:
        from app.bot.keyboards_ecosystem import insufficient_credits_kb

        await loading.edit_text(body, reply_markup=insufficient_credits_kb(lang))
        return
    if consume:
        await consume_music_operation(session, user, separate=False)
    header = {"analyze": "mus_analyze_result", "translate": "mus_translate_result", "chords": "mus_chords_result"}.get(
        action, "mus_result"
    )
    await deliver_long_text(loading, f"{t(lang, header)}\n\n{body}", reply_markup=music_after_lyrics_kb(lang))


@router.message(MusicStates.waiting_lyrics_text, F.text)
async def music_lyrics_text(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if await _music_quota_blocked(message, user, session):
        return
    data = await state.get_data()
    action = data.get("mus_action", "analyze")
    lyrics = (message.text or "").strip()
    if not lyrics:
        return
    await state.update_data(last_lyrics=lyrics)
    lang = user.language
    await _run_text_action(message, bot, user, session, action, lyrics, lang)
    await state.set_state(None)


@router.message(MusicStates.waiting_audio)
async def music_waiting_audio(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if await _music_quota_blocked(message, user, session):
        return
    audio = audio_from_message(message)
    if not audio:
        await message.answer(t(user.language, "mus_need_audio"), reply_markup=music_cancel_kb(user.language))
        return

    file_id, filename = audio
    data = await state.get_data()
    action = data.get("mus_action", "lyrics")
    mode = data.get("mus_mode", "lyrics")
    lang = user.language
    loading = await message.answer(t(lang, "mus_processing"))

    try:
        if action == "separate":
            if await _music_quota_blocked(message, user, session, separate=True):
                return
            await _handle_separate(message, loading, bot, file_id, filename, mode, lang)
            await consume_music_operation(session, user, separate=True)
            await state.clear()
            return

        lyrics = await transcribe_song_lyrics(bot, file_id, filename)
        if not lyrics:
            await loading.edit_text(t(lang, "mus_transcribe_failed"))
            return

        await consume_music_operation(session, user, separate=False)

        title = ""
        if message.audio and message.audio.title:
            performer = message.audio.performer or ""
            title = f"{performer} — {message.audio.title}".strip(" —")

        await state.update_data(last_lyrics=lyrics, last_title=title or filename)

        if action == "lyrics" or mode == "lyrics":
            text = f"{t(lang, 'mus_lyrics_result')}\n\n{lyrics}"
            await deliver_long_text(loading, text, reply_markup=music_after_lyrics_kb(lang))
            await state.set_state(None)
            return

        await loading.delete()
        await _run_text_action(message, bot, user, session, action, lyrics, lang, consume=False)
        await state.set_state(None)
    except Exception:
        logger.exception("Music audio processing failed")
        await loading.edit_text(t(lang, "mus_error"))


async def _handle_separate(
    message: Message,
    loading: Message,
    bot: Bot,
    file_id: str,
    filename: str,
    mode: str,
    lang: str,
) -> None:
    raw = await download_audio_bytes(bot, file_id)
    vocals, instrumental, err = await separate_audio(raw, filename, mode)
    if err == "no_ffmpeg":
        await loading.edit_text(t(lang, "mus_no_ffmpeg"))
        return
    if err:
        await loading.edit_text(t(lang, "mus_separate_failed"))
        return

    await loading.edit_text(t(lang, "mus_separate_done"))
    if vocals and mode in {"vocal", "both"}:
        await message.answer_audio(
            BufferedInputFile(vocals, filename="vocals.mp3"),
            title=t(lang, "mus_vocal_title"),
        )
    if instrumental and mode in {"instrumental", "both"}:
        await message.answer_audio(
            BufferedInputFile(instrumental, filename="instrumental.mp3"),
            title=t(lang, "mus_instrumental_title"),
        )
    await message.answer(t(lang, "mus_separate_hint"), reply_markup=music_sub_kb("separate", lang))
