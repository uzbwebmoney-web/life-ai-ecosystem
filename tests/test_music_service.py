import pytest

from app.services.music_service import (
    audio_from_message,
    build_analyze_prompt,
    build_chords_prompt,
    build_translate_prompt,
    clean_whisper_lyrics,
    compact_repeated_lines,
    detect_song_language_from_text,
    normalize_song_language,
    separate_audio,
    validate_lyrics_transcription,
)


class _Audio:
    def __init__(self, file_id: str, file_name: str | None = None, title: str | None = None):
        self.file_id = file_id
        self.file_name = file_name
        self.file_unique_id = "uniq"
        self.title = title
        self.performer = None


class _Doc:
    def __init__(self, file_id: str, mime_type: str, file_name: str):
        self.file_id = file_id
        self.mime_type = mime_type
        self.file_name = file_name


class _Msg:
    def __init__(self, audio=None, document=None, voice=None):
        self.audio = audio
        self.document = document
        self.voice = voice


def test_audio_from_message_track():
    msg = _Msg(audio=_Audio("fid1", "song.mp3", title="Test"))
    assert audio_from_message(msg) == ("fid1", "song.mp3")


def test_audio_from_message_document():
    msg = _Msg(document=_Doc("fid2", "audio/mpeg", "track.m4a"))
    assert audio_from_message(msg) == ("fid2", "track.m4a")


def test_build_prompts_contain_lyrics():
    lyrics = "Hello world song"
    assert lyrics in build_analyze_prompt(lyrics, "en", "ru")
    assert lyrics in build_translate_prompt(lyrics, "uz", "en")
    assert lyrics in build_chords_prompt(lyrics, "uz")


@pytest.mark.asyncio
async def test_separate_audio_invalid_mode():
    vocals, inst, err = await separate_audio(b"fake", "x.mp3", "nope")
    assert err == "invalid_mode"
    assert vocals is None and inst is None


def test_clean_whisper_strips_prompt_leak():
    raw = "Куплет и припев. Только слова. Alvon alvon gullaring olib"
    assert clean_whisper_lyrics(raw).startswith("Alvon")


def test_compact_repeated_lines_limits_chorus():
    raw = "Ko'k jiguli. Ko'k jiguli. Ko'k jiguli. Ko'k jiguli."
    out = compact_repeated_lines(raw, max_same_line=2)
    assert out.count("Ko'k jiguli") == 2


def test_validate_lyrics_rejects_music_emoji_garbage():
    assert validate_lyrics_transcription("🎵🎵🎵 🎵🎵🎵 🎵🎵🎵") is None


def test_validate_lyrics_rejects_whisper_loop_hallucination():
    garbage = " ".join(["Альван", "Альван", "Гулярин"] * 8)
    assert validate_lyrics_transcription(garbage, song_lang="uz") is None


def test_normalize_song_language_from_whisper_uz():
    assert normalize_song_language("uz", "Alvon alvon gullaring") == "uz"
    assert normalize_song_language("tr", "elvan gullaring") == "uz"
    assert normalize_song_language(None, "text", hint="uz") == "uz"


def test_whisper_api_language_skips_uz():
    from app.services.media_ai import whisper_api_language

    assert whisper_api_language("uz") is None
    assert whisper_api_language("ru") == "ru"
    assert whisper_api_language("en") == "en"


def test_detect_song_language_uzbek_markers():
    assert detect_song_language_from_text("Ko'k jiguli qo'shni Guli yodimda") == "uz"


def test_validate_lyrics_accepts_real_text():
    text = "Я иду по улице в тихий вечерний час"
    assert validate_lyrics_transcription(text, song_lang="ru") == text


def test_validate_lyrics_accepts_uzbek_latin():
    text = "Alvon alvon gullaring olib atrofingga nazarlar solar eding"
    assert validate_lyrics_transcription(text, song_lang="uz") == text


def test_validate_lyrics_rejects_repeated_word():
    assert validate_lyrics_transcription("music music music music music music") is None


def test_validate_lyrics_rejects_whisper_hallucination():
    assert validate_lyrics_transcription("Thanks for watching!") is None


def test_music_module_in_catalog():
    from app.core.modules.catalog import MODULE_BY_ID

    mod = MODULE_BY_ID["music"]
    assert mod.emoji == "🎵"
    assert len(mod.submodules) >= 5
