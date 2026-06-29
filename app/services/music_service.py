from __future__ import annotations

import asyncio
import io
import logging
import re
import shutil
import tempfile
from pathlib import Path

from aiogram import Bot
from aiogram.types import Message

from app.services.media_ai import transcribe_audio_bytes

logger = logging.getLogger(__name__)

AUDIO_MIME_PREFIX = "audio/"
AUDIO_EXTENSIONS = frozenset({".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".opus", ".wma"})

_LYRICS_PROMPTS: dict[str, str] = {
    "ru": "Текст песни, только слова вокала, без описания музыки.",
    "uz": "Qo'shiq matni, faqat vokal so'zlari.",
    "en": "Song lyrics, sung words only, no instrumental description.",
}

_WHISPER_HALLUCINATION_RE = re.compile(
    r"(thanks for watching|please subscribe|subtitles by|amara\.org|"
    r"субтитр|подписывайтесь|subscribe to)",
    re.IGNORECASE,
)

MUSIC_SUBMODULE_AI: dict[str, str] = {
    "lyrics": "Распознавай текст песни из аудио максимально точно, сохраняя строфы и припевы.",
    "separate": "Объясняй разделение вокала и инструментала; качество зависит от микса трека.",
    "analyze": "Определи жанр, настроение, темп (BPM), инструменты, язык и краткое описание.",
    "translate": "Переводи текст песни, сохраняя рифму и смысл по возможности.",
    "chords": "Подбери тональность и последовательность аккордов по тексту/описанию.",
    "collection": "Помогай вести коллекцию треков — название, исполнитель, заметки.",
}

SEPARATE_MODES = frozenset({"vocal", "instrumental", "both"})


def validate_lyrics_transcription(text: str) -> str | None:
    """Return cleaned lyrics or None if Whisper output is noise / instrumental hallucination."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    if _WHISPER_HALLUCINATION_RE.search(cleaned):
        return None
    cleaned = re.sub(r"^[\s♪🎵🎶🎤•\-\.…]+", "", cleaned)
    cleaned = re.sub(r"[\s♪🎵🎶]+$", "", cleaned).strip()
    if not cleaned:
        return None
    letters = sum(1 for c in cleaned if c.isalpha())
    if letters < 12:
        return None
    compact = re.sub(r"\s+", "", cleaned)
    if not compact or letters / len(compact) < 0.55:
        return None
    tokens = re.findall(r"\w+", cleaned, flags=re.UNICODE)
    if len(tokens) < 3:
        return None
    if len(tokens) >= 5:
        lowered = [tok.lower() for tok in tokens]
        top = max(lowered.count(word) for word in set(lowered))
        if top / len(tokens) > 0.7:
            return None
    return cleaned


def music_submodule_description(sub_id: str, lang: str) -> str:
    from app.core.i18n import t

    key = f"mus_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else MUSIC_SUBMODULE_AI.get(sub_id, "")


def audio_from_message(message: Message) -> tuple[str, str] | None:
    if message.audio:
        name = message.audio.file_name or f"track_{message.audio.file_unique_id}.mp3"
        return message.audio.file_id, name
    doc = message.document
    if doc:
        mime = (doc.mime_type or "").lower()
        name = doc.file_name or "audio.mp3"
        ext = Path(name).suffix.lower()
        if mime.startswith(AUDIO_MIME_PREFIX) or mime in {"application/ogg"} or ext in AUDIO_EXTENSIONS:
            return doc.file_id, name
    if message.voice:
        return message.voice.file_id, "voice.ogg"
    return None


async def download_audio_bytes(bot: Bot, file_id: str) -> bytes:
    file = await bot.get_file(file_id)
    buffer = io.BytesIO()
    await bot.download_file(file.file_path, buffer)
    return buffer.getvalue()


async def transcribe_song_lyrics(bot: Bot, file_id: str, filename: str, *, lang: str = "ru") -> str | None:
    data = await download_audio_bytes(bot, file_id)
    code = lang if lang in _LYRICS_PROMPTS else "ru"
    raw = await transcribe_audio_bytes(
        data,
        filename,
        prompt=_LYRICS_PROMPTS[code],
        lang=code,
        lyrics_mode=True,
    )
    if not raw:
        return None
    return validate_lyrics_transcription(raw)


async def _run_ffmpeg(args: list[str]) -> bool:
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.warning("ffmpeg failed (%s): %s", proc.returncode, stderr.decode(errors="replace")[:500])
            return False
        return True
    except FileNotFoundError:
        return False


async def separate_audio(
    audio_bytes: bytes,
    filename: str,
    mode: str,
) -> tuple[bytes | None, bytes | None, str | None]:
    """Split track into vocal and instrumental stems via ffmpeg center/side extraction."""
    if mode not in SEPARATE_MODES:
        return None, None, "invalid_mode"
    if not shutil.which("ffmpeg"):
        return None, None, "no_ffmpeg"

    ext = Path(filename).suffix.lower() or ".mp3"
    if ext not in AUDIO_EXTENSIONS:
        ext = ".mp3"

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"input{ext}"
        vocal_path = Path(tmp) / "vocals.mp3"
        inst_path = Path(tmp) / "instrumental.mp3"
        src.write_bytes(audio_bytes)

        stereo = "aformat=channel_layouts=stereo"
        vocal_filter = f"{stereo},pan=mono|c0=0.5*c0+0.5*c1"
        inst_filter = f"{stereo},pan=stereo|c0=c0-c1|c1=c1-c0"

        vocal_ok = await _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-af",
                vocal_filter,
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(vocal_path),
            ]
        )
        inst_ok = await _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-af",
                inst_filter,
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(inst_path),
            ]
        )

        vocals: bytes | None = vocal_path.read_bytes() if vocal_ok and vocal_path.exists() else None
        instrumental: bytes | None = inst_path.read_bytes() if inst_ok and inst_path.exists() else None

        if mode == "vocal":
            return vocals, None, None if vocals else "separate_failed"
        if mode == "instrumental":
            return None, instrumental, None if instrumental else "separate_failed"
        if not vocals and not instrumental:
            return None, None, "separate_failed"
        return vocals, instrumental, None


def build_analyze_prompt(lyrics: str, lang: str) -> str:
    lang_label = {"ru": "русском", "uz": "узбекском", "en": "English"}.get(lang, lang)
    return (
        f"Проанализируй музыкальный трек по распознанному тексту. Ответ на {lang_label} языке.\n"
        "Укажи: жанр, настроение, примерный BPM, язык песни, основные инструменты, "
        "краткое описание (2–3 предложения).\n\n"
        f"Текст:\n{lyrics[:6000]}"
    )


def build_translate_prompt(lyrics: str, lang: str) -> str:
    lang_label = {"ru": "русский", "uz": "узбекский", "en": "английский"}.get(lang, "русский")
    return (
        f"Переведи текст песни на {lang_label}. Сохраняй строфы и припевы. "
        "Если строка неясна — оставь пометку [?].\n\n"
        f"{lyrics[:6000]}"
    )


def build_chords_prompt(lyrics: str, lang: str) -> str:
    lang_label = {"ru": "русском", "uz": "узбекском", "en": "English"}.get(lang, lang)
    return (
        f"По тексту песни предложи тональность и аккорды (формат Am, F, C, G). "
        f"Ответ на {lang_label}. Укажи схему для куплета и припева отдельно.\n\n"
        f"{lyrics[:6000]}"
    )
