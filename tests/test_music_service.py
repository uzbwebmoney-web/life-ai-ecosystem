import pytest

from app.services.music_service import (
    audio_from_message,
    build_analyze_prompt,
    build_chords_prompt,
    build_translate_prompt,
    separate_audio,
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
    assert lyrics in build_analyze_prompt(lyrics, "ru")
    assert lyrics in build_translate_prompt(lyrics, "en")
    assert lyrics in build_chords_prompt(lyrics, "uz")


@pytest.mark.asyncio
async def test_separate_audio_invalid_mode():
    vocals, inst, err = await separate_audio(b"fake", "x.mp3", "nope")
    assert err == "invalid_mode"
    assert vocals is None and inst is None


def test_music_module_in_catalog():
    from app.core.modules.catalog import MODULE_BY_ID

    mod = MODULE_BY_ID["music"]
    assert mod.emoji == "🎵"
    assert len(mod.submodules) >= 5
