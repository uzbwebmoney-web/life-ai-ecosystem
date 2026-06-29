from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb, dashboard_kb
from app.bot.message_ui import deliver_long_text
from app.core.i18n import t
from app.models.entities import User
from app.services.workspace_rag_service import ingest_workspace_document, list_workspace_documents

router = Router()


async def index_telegram_document(
    message: Message,
    bot: Bot,
    user: User,
    session: AsyncSession,
    *,
    shared: bool = False,
    notify: bool = True,
) -> WorkspaceDocument | None:
    """Download and index a Telegram document."""
    from app.models.entities import WorkspaceDocument

    doc = message.document
    if not doc:
        return None
    name = (doc.file_name or "document").lower()
    if not any(name.endswith(ext) for ext in (".pdf", ".docx", ".doc", ".txt", ".md")):
        return None
    try:
        file = await bot.get_file(doc.file_id)
        from io import BytesIO

        buf = BytesIO()
        await bot.download_file(file.file_path, buf)
        data = buf.getvalue()
        if not data:
            return None
        indexed = await ingest_workspace_document(
            session,
            user,
            title=doc.file_name or "Document",
            filename=doc.file_name or "document",
            mime_type=doc.mime_type or "",
            file_bytes=data,
            telegram_file_id=doc.file_id,
            shared=shared,
        )
        if notify:
            await message.answer(
                t(user.language, "workspace_indexed", title=indexed.title, chars=indexed.char_count),
                reply_markup=back_menu_kb(user.language),
            )
        return indexed
    except Exception:
        return None

