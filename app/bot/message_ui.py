from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

TELEGRAM_TEXT_LIMIT = 4096
TELEGRAM_SAFE_LIMIT = 4000


def split_telegram_text(text: str, *, limit: int = TELEGRAM_SAFE_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    block = ""
    for line in text.split("\n"):
        candidate = f"{block}\n{line}" if block else line
        if len(candidate) <= limit:
            block = candidate
            continue
        if block:
            chunks.append(block)
        while len(line) > limit:
            chunks.append(line[:limit])
            line = line[limit:]
        block = line
    if block:
        chunks.append(block)
    return chunks or [text[:limit]]


async def edit_or_answer_text(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = "HTML",
) -> None:
    kwargs: dict = {"reply_markup": reply_markup}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    if message.text:
        try:
            await message.edit_text(text, **kwargs)
            return
        except TelegramBadRequest:
            pass
    await message.answer(text, **kwargs)


async def deliver_long_text(
    anchor: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = "HTML",
) -> None:
    chunks = split_telegram_text(text)
    kwargs: dict = {}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode

    if len(chunks) == 1:
        try:
            await anchor.edit_text(chunks[0], reply_markup=reply_markup, **kwargs)
            return
        except TelegramBadRequest:
            await anchor.answer(chunks[0], reply_markup=reply_markup, **kwargs)
            return

    try:
        await anchor.edit_text(chunks[0], **kwargs)
    except TelegramBadRequest:
        await anchor.answer(chunks[0], **kwargs)

    for chunk in chunks[1:-1]:
        await anchor.answer(chunk, **kwargs)
    await anchor.answer(chunks[-1], reply_markup=reply_markup, **kwargs)
