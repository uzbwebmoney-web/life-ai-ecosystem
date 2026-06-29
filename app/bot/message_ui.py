from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

TELEGRAM_TEXT_LIMIT = 4096
TELEGRAM_SAFE_LIMIT = 4000


def _is_not_modified_error(exc: TelegramBadRequest) -> bool:
    return "message is not modified" in (exc.message or "").lower()


def _is_stale_callback_error(exc: TelegramBadRequest) -> bool:
    msg = (exc.message or "").lower()
    return "query is too old" in msg or "query id is invalid" in msg


async def safe_callback_answer(callback, *args, **kwargs) -> None:
    try:
        await callback.answer(*args, **kwargs)
    except TelegramBadRequest as exc:
        if _is_stale_callback_error(exc):
            return
        raise


async def safe_edit_text(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = "HTML",
) -> bool:
    """Edit message text; return True if edited. No-op when content is unchanged."""
    if not message.text and not message.caption:
        return False
    kwargs: dict = {"reply_markup": reply_markup}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    try:
        await message.edit_text(text, **kwargs)
        return True
    except TelegramBadRequest as exc:
        if _is_not_modified_error(exc):
            return False
        raise


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
        except TelegramBadRequest as exc:
            if _is_not_modified_error(exc):
                return
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
        except TelegramBadRequest as exc:
            if _is_not_modified_error(exc):
                return
            await anchor.answer(chunks[0], reply_markup=reply_markup, **kwargs)
            return

    try:
        await anchor.edit_text(chunks[0], **kwargs)
    except TelegramBadRequest as exc:
        if not _is_not_modified_error(exc):
            await anchor.answer(chunks[0], **kwargs)

    for chunk in chunks[1:-1]:
        await anchor.answer(chunk, **kwargs)
    await anchor.answer(chunks[-1], reply_markup=reply_markup, **kwargs)
