from __future__ import annotations

from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import User
from app.services.study_document_service import (
    ExportFormat,
    build_document_bytes,
    detect_export_format,
    extract_document_title,
    get_last_study_document,
    is_format_only_request,
    store_last_study_document,
    strip_export_disclaimers,
)
from app.services.subscription_service import check_pdf_export_quota, consume_pdf_export


async def export_last_study_document(
    message: Message,
    user: User,
    session: AsyncSession,
    *,
    fmt: ExportFormat,
) -> None:
    cached = get_last_study_document(user.id)
    if not cached:
        await message.answer(t(user.language, "edu_export_no_previous"))
        return
    await _send_study_document(
        message,
        user,
        session,
        title=cached["title"],
        body=cached["body"],
        fmt=fmt,
    )


async def try_format_only_export(message: Message, user: User, session: AsyncSession, text: str) -> bool:
    fmt = detect_export_format(text)
    if not fmt or not is_format_only_request(text):
        return False
    cached = get_last_study_document(user.id)
    if not cached:
        await message.answer(t(user.language, "edu_export_no_previous"))
        return True
    await _send_study_document(
        message,
        user,
        session,
        title=cached["title"],
        body=cached["body"],
        fmt=fmt,
    )
    return True


async def after_study_ai_response(
    message: Message,
    user: User,
    session: AsyncSession,
    *,
    user_text: str,
    answer: str,
    module_id: str,
    submodule_id: str | None,
) -> None:
    if module_id != "education":
        return
    clean_answer = strip_export_disclaimers(answer)
    title = extract_document_title(user_text, clean_answer)
    store_last_study_document(
        user.id,
        title=title,
        body=clean_answer,
        query=user_text,
    )
    fmt = detect_export_format(user_text)
    if not fmt:
        return
    await _send_study_document(
        message,
        user,
        session,
        title=title,
        body=clean_answer,
        fmt=fmt,
    )


async def _send_study_document(
    message: Message,
    user: User,
    session: AsyncSession,
    *,
    title: str,
    body: str,
    fmt: ExportFormat,
) -> None:
    lang = user.language
    if fmt in {"pdf", "docx"}:
        quota_msg = await check_pdf_export_quota(session, user, lang=lang)
        if quota_msg:
            await message.answer(quota_msg)
            return
    try:
        data, filename = build_document_bytes(title, body, fmt)
    except Exception:
        await message.answer(t(lang, "edu_export_failed"))
        return
    if fmt in {"pdf", "docx"}:
        await consume_pdf_export(session, user)
    label = t(lang, f"edu_export_format_{fmt}")
    await message.answer_document(
        BufferedInputFile(data, filename=filename),
        caption=t(lang, "edu_export_sent", format=label, title=title[:120]),
    )
