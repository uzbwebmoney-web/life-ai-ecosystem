from __future__ import annotations

import asyncio
import io
import logging
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot
from aiogram.types import Message

from app.services.media_ai import WhisperLyricsResult, transcribe_lyrics_detailed

logger = logging.getLogger(__name__)

AUDIO_MIME_PREFIX = "audio/"
AUDIO_EXTENSIONS = frozenset({".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".opus", ".wma"})

_LYRICS_STYLE: dict[str, str] = {
    "uz": "Alvon alvon gullaring olib, atrofingga nazarlar solar eding, ko'k jiguli qo'shni Guli.",
    "ru": "В тихий вечер за окном, поют соловьи, только слова песни.",
    "en": "Love song lyrics, singing words, verse and chorus.",
}

_PROMPT_LEAK_RE = re.compile(
    r"^("
    r"куплет и припев[\.!]?\s*только слова[\.!]?\s*|"
    r"текст песни[,\s]*только слова[^.]*\.?\s*|"
    r"o'zbek qo'shiq[^.]*\.?\s*|"
    r"song lyrics line by line[^.]*\.?\s*"
    r")+",
    re.IGNORECASE,
)
_MUSIC_LABEL_RE = re.compile(r"\b(?:müzik|muzik(?:ani)?|music)\b", re.IGNORECASE)

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

SUPPORTED_SONG_LANGS = frozenset({"ru", "uz", "en"})

_WHISPER_LANG_MAP: dict[str, str] = {
    "uz": "uz",
    "ru": "ru",
    "en": "en",
    "tr": "uz",
    "az": "uz",
    "kk": "uz",
    "ky": "uz",
    "tg": "uz",
}

_UZ_TEXT_MARKERS = re.compile(
    r"\b(?:o'|g'|qo'y|gullar|yodimda|kelar|atrof|jiguli|qizg'on|sevgi|mendan|yonimda)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SongLyricsTranscription:
    text: str
    song_lang: str


def _tokenize_lyrics(text: str) -> list[str]:
    return re.findall(r"\w+", text, flags=re.UNICODE)


def _is_repetitive_phrase(tokens: list[str]) -> bool:
    if len(tokens) < 8:
        return False
    lowered = [tok.lower() for tok in tokens]
    for size in range(2, 6):
        counts: dict[tuple[str, ...], int] = {}
        for i in range(len(lowered) - size + 1):
            phrase = tuple(lowered[i : i + size])
            counts[phrase] = counts.get(phrase, 0) + 1
        if counts:
            _, count = max(counts.items(), key=lambda item: item[1])
            if count >= 4 and count * size >= len(lowered) * 0.4:
                return True
        i = 0
        while i + size * 2 <= len(lowered):
            phrase = tuple(lowered[i : i + size])
            reps = 1
            j = i + size
            while j + size <= len(lowered) and tuple(lowered[j : j + size]) == phrase:
                reps += 1
                j += size
            if reps >= 4:
                return True
            i += 1
    return False


def _uz_latin_script_expected(cleaned: str, song_lang: str) -> bool:
    if song_lang != "uz":
        return True
    cyr = sum(1 for c in cleaned if "\u0400" <= c <= "\u04FF")
    if cyr < 15:
        return True
    lat = sum(1 for c in cleaned if c.isalpha() and not ("\u0400" <= c <= "\u04FF"))
    return lat >= cyr


def clean_whisper_lyrics(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = _PROMPT_LEAK_RE.sub("", cleaned).strip()
    cleaned = _MUSIC_LABEL_RE.sub("", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.])", r"\1", cleaned)
    return cleaned.strip()


def compact_repeated_lines(text: str, *, max_same_line: int = 4) -> str:
    """Drop only excessive identical lines; keep most of the song intact."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    lines = [p.strip() for p in parts if p.strip()]
    counts: dict[str, int] = {}
    kept: list[str] = []
    for line in lines:
        key = line.lower()
        counts[key] = counts.get(key, 0) + 1
        if counts[key] <= max_same_line:
            kept.append(line)
    return "\n".join(kept)


def _whisper_attempts() -> list[tuple[str, str | None]]:
    """Language-agnostic attempts: auto-detect first, then common song languages."""
    return [
        (_LYRICS_STYLE["uz"], None),
        (_LYRICS_STYLE["uz"], "uz"),
        (_LYRICS_STYLE["ru"], "ru"),
        (_LYRICS_STYLE["en"], "en"),
        (_LYRICS_STYLE["ru"], None),
    ]


def detect_song_language_from_text(text: str) -> str | None:
    cleaned = (text or "").lower()
    if not cleaned:
        return None
    cyr = sum(1 for c in cleaned if "\u0400" <= c <= "\u04FF")
    lat = sum(1 for c in cleaned if c.isalpha() and not ("\u0400" <= c <= "\u04FF"))
    if cyr > lat and cyr >= 10:
        return "ru"
    if _UZ_TEXT_MARKERS.search(cleaned):
        return "uz"
    if re.search(r"\b(?:the|and|you|love|heart|baby)\b", cleaned):
        return "en"
    if lat >= 10 and re.search(r"\b(?:va|ham|sen|men|yurak|sevgi|qo'sh|gul)\b", cleaned):
        return "uz"
    return None


def normalize_song_language(detected: str | None, text: str, *, hint: str | None = None) -> str:
    from_text = detect_song_language_from_text(text)
    if from_text:
        return from_text
    code = (detected or "").strip().lower()
    if hint == "uz":
        return "uz"
    if code in _WHISPER_LANG_MAP:
        return _WHISPER_LANG_MAP[code]
    return "en"


def _score_transcription(metrics: WhisperLyricsResult, song_lang: str, whisper_lang: str | None) -> float:
    score = float(len(metrics.text or ""))
    score += len(metrics.text or "") * 0.35
    if metrics.avg_logprob is not None:
        score += (metrics.avg_logprob + 1.0) * 40
    if whisper_lang is None:
        score += 15
    if whisper_lang == song_lang:
        score += 25
    if metrics.detected_language and normalize_song_language(metrics.detected_language, metrics.text) == song_lang:
        score += 20
    return score


def song_language_label(song_lang: str, ui_lang: str) -> str:
    from app.core.i18n import t

    key = f"mus_song_lang_{song_lang}"
    label = t(ui_lang, key)
    return label if label != key else song_lang


def build_polish_lyrics_prompt(raw: str, lang: str) -> str:
    if lang == "uz":
        target = "узбекской латинице (o', g', qo'sh, ko'k jiguli)"
    elif lang == "en":
        target = "English"
    else:
        target = "русском"
    body = raw[:12000]
    return (
        f"Ниже — расшифровка песни (Whisper), возможно по частям. Приведи к полному читаемому тексту на {target}.\n"
        "Правила:\n"
        "- Сохрани ВСЕ уникальные строки и куплеты из расшифровки — ничего не пропускай и не сокращай\n"
        "- Исправь фонетику (elvan→Alvon, güllerin→gullaring, ko'k jiguli, qo'shni Guli, eslatadi)\n"
        "- Одинаковый припев оставь максимум 2 раза; уникальные куплеты — все\n"
        "- Не придумывай новые куплеты, которых нет в расшифровке\n"
        "- Формат: по строке, пустая строка между куплетами\n\n"
        f"Расшифровка:\n{body}"
    )


async def polish_lyrics_with_ai(
    raw: str,
    *,
    song_lang: str,
    ui_lang: str,
    session,
    user,
    bot,
) -> str:
    from app.services.ai_service import ask_ai
    from app.services.module_context import build_module_ai_hint
    from app.services.subscription_service import parse_insufficient_credits_reply

    if not raw.strip():
        return raw
    snippet = raw[:150].replace("\n", " ").strip()
    if len(raw) > 150:
        snippet += "…"
    from app.core.i18n import t

    admin_preview = t(ui_lang, "mus_admin_ai_preview", snippet=snippet)
    answer = await ask_ai(
        user_message=build_polish_lyrics_prompt(raw, song_lang),
        module_hint=build_module_ai_hint("music", "lyrics", lang=ui_lang),
        language=ui_lang,
        session=session,
        user=user,
        bot=bot,
        module_id="music",
        submodule_id="lyrics",
        max_completion_tokens=4500,
        usage_source="music_lyrics",
        admin_preview=admin_preview,
    )
    is_quota, body = parse_insufficient_credits_reply(answer)
    if is_quota or not body.strip():
        return raw
    return body.strip()


async def finalize_song_lyrics(
    raw: str,
    *,
    song_lang: str,
    ui_lang: str,
    session,
    user,
    bot,
) -> str:
    cleaned = clean_whisper_lyrics(raw)
    if not cleaned:
        return raw
    return await polish_lyrics_with_ai(
        cleaned,
        song_lang=song_lang,
        ui_lang=ui_lang,
        session=session,
        user=user,
        bot=bot,
    )


async def _audio_duration_seconds(data: bytes, filename: str) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    ext = Path(filename).suffix.lower() or ".mp3"
    if ext not in AUDIO_EXTENSIONS:
        ext = ".mp3"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"in{ext}"
        src.write_bytes(data)
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(src),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode != 0 or not stdout.strip():
                return None
            return float(stdout.decode().strip())
        except (ValueError, OSError):
            return None


async def _split_audio_to_chunks(data: bytes, filename: str, *, segment_sec: int = 70) -> list[bytes]:
    if not shutil.which("ffmpeg"):
        return [data]
    ext = Path(filename).suffix.lower() or ".mp3"
    if ext not in AUDIO_EXTENSIONS:
        ext = ".mp3"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"in{ext}"
        src.write_bytes(data)
        out_tpl = str(Path(tmp) / "part_%03d.mp3")
        ok = await _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-f",
                "segment",
                "-segment_time",
                str(segment_sec),
                "-reset_timestamps",
                "1",
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "4",
                out_tpl,
            ]
        )
        if not ok:
            return [data]
        parts = sorted(Path(tmp).glob("part_*.mp3"))
        if len(parts) <= 1:
            return [data]
        return [p.read_bytes() for p in parts]


async def _transcribe_buffer_attempts(buffer: io.BytesIO, filename: str) -> SongLyricsTranscription | None:
    best: SongLyricsTranscription | None = None
    best_score = float("-inf")
    for prompt, whisper_lang in _whisper_attempts():
        buffer.seek(0)
        try:
            metrics = await transcribe_lyrics_detailed(buffer, prompt=prompt, lang=whisper_lang)
        except Exception:
            logger.exception("Whisper attempt failed (lang=%s)", whisper_lang)
            continue
        if not metrics.text:
            continue
        song_lang = normalize_song_language(metrics.detected_language, metrics.text, hint=whisper_lang)
        cleaned = clean_whisper_lyrics(metrics.text)
        validated = validate_lyrics_transcription(cleaned, song_lang=song_lang, metrics=metrics)
        if not validated:
            continue
        score = _score_transcription(metrics, song_lang, whisper_lang)
        if score > best_score:
            best_score = score
            best = SongLyricsTranscription(text=validated, song_lang=song_lang)
    return best


async def _transcribe_chunked(data: bytes, filename: str) -> SongLyricsTranscription | None:
    chunks = await _split_audio_to_chunks(data, filename)
    if len(chunks) <= 1:
        return None
    parts: list[str] = []
    for idx, chunk in enumerate(chunks):
        buf = io.BytesIO(chunk)
        buf.name = f"{Path(filename).stem}_part{idx}.mp3"
        piece = await _transcribe_buffer_attempts(buf, buf.name)
        if piece and piece.text:
            parts.append(piece.text)
    if not parts:
        return None
    merged = "\n".join(parts)
    song_lang = normalize_song_language(None, merged)
    cleaned = clean_whisper_lyrics(merged)
    validated = validate_lyrics_transcription(cleaned, song_lang=song_lang)
    if not validated:
        return None
    return SongLyricsTranscription(text=validated, song_lang=song_lang)


def validate_lyrics_transcription(
    text: str,
    *,
    song_lang: str = "ru",
    metrics: WhisperLyricsResult | None = None,
) -> str | None:
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
    if metrics:
        if metrics.avg_no_speech is not None and metrics.avg_no_speech > 0.55:
            letters = sum(1 for c in cleaned if c.isalpha())
            if letters < 25:
                return None
        if metrics.compression_ratio is not None and metrics.compression_ratio > 2.15:
            return None
        if metrics.avg_logprob is not None and metrics.avg_logprob < -1.0:
            return None
    letters = sum(1 for c in cleaned if c.isalpha())
    if letters < 12:
        return None
    compact = re.sub(r"\s+", "", cleaned)
    if not compact or letters / len(compact) < 0.55:
        return None
    tokens = _tokenize_lyrics(cleaned)
    if len(tokens) < 3:
        return None
    if len(tokens) >= 5:
        lowered = [tok.lower() for tok in tokens]
        top = max(lowered.count(word) for word in set(lowered))
        if top / len(tokens) > 0.7:
            return None
    if _is_repetitive_phrase(tokens):
        return None
    if not _uz_latin_script_expected(cleaned, song_lang):
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


async def transcribe_song_lyrics(bot: Bot, file_id: str, filename: str) -> SongLyricsTranscription | None:
    data = await download_audio_bytes(bot, file_id)
    filename = filename or "audio.mp3"
    buffer = io.BytesIO(data)
    buffer.name = filename

    best = await _transcribe_buffer_attempts(buffer, filename)

    duration = await _audio_duration_seconds(data, filename)
    if duration is None or duration > 90:
        chunked = await _transcribe_chunked(data, filename)
        if chunked and (not best or len(chunked.text) > len(best.text) * 1.1):
            return chunked
    return best


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


def build_analyze_prompt(lyrics: str, song_lang: str, ui_lang: str) -> str:
    lang_label = {"ru": "русском", "uz": "узбекском", "en": "English"}.get(ui_lang, ui_lang)
    song_label = {"ru": "русская", "uz": "узбекская", "en": "английская"}.get(song_lang, song_lang)
    return (
        f"Проанализируй музыкальный трек. Текст песни на {song_label} языке. Ответ на {lang_label}.\n"
        "Укажи: жанр, настроение, примерный BPM, язык песни, основные инструменты, "
        "краткое описание (2–3 предложения).\n\n"
        f"Текст:\n{lyrics[:6000]}"
    )


def build_translate_prompt(lyrics: str, song_lang: str, ui_lang: str) -> str:
    song_label = {"ru": "русского", "uz": "узбекского", "en": "английского"}.get(song_lang, song_lang)
    target = {"ru": "русский", "uz": "узбекский", "en": "английский"}.get(ui_lang, ui_lang)
    return (
        f"Переведи текст песни с {song_label} на {target}. Сохраняй строфы и припевы. "
        "Если строка неясна — оставь пометку [?].\n\n"
        f"{lyrics[:6000]}"
    )


def build_chords_prompt(lyrics: str, ui_lang: str) -> str:
    lang_label = {"ru": "русском", "uz": "узбекском", "en": "English"}.get(ui_lang, ui_lang)
    return (
        f"По тексту песни предложи тональность и аккорды (формат Am, F, C, G). "
        f"Ответ на {lang_label}. Укажи схему для куплета и припева отдельно.\n\n"
        f"{lyrics[:6000]}"
    )
