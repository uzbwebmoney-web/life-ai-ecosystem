from __future__ import annotations

from aiogram.types import BufferedInputFile, Message

from app.models.entities import User
from app.services.media_ai import synthesize_speech
from app.services.subscription_service import parse_insufficient_credits_reply


def voice_snippet(text: str, *, max_chars: int = 500) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[:max_chars]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.strip() + "…"


async def maybe_send_voice_reply(message: Message, user: User, answer: str) -> None:
    if not user.voice_mode:
        return
    if not answer.strip():
        return
    is_quota, _ = parse_insufficient_credits_reply(answer)
    if is_quota:
        return
    audio = await synthesize_speech(voice_snippet(answer))
    if not audio:
        return
    await message.answer_voice(BufferedInputFile(audio, filename="reply.ogg"))
