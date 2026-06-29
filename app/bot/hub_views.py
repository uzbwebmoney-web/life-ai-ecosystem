from __future__ import annotations

from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import back_menu_kb, dashboard_kb, projects_kb
from app.bot.message_ui import deliver_long_text, safe_edit_text
from app.core.i18n import t
from app.models.entities import User
from app.services.project_service import create_project, get_active_project, list_projects
from app.services.subscription_service import check_export_allowed, ensure_user_subscription_fields
from app.services.today_service import build_today_dashboard
from app.services.vault_lock_service import is_vault_protected, is_vault_unlocked
from app.services.workspace_rag_service import list_workspace_documents


async def show_today(
    target: Message | CallbackQuery,
    user: User,
    session: AsyncSession,
    *,
    edit: bool = False,
) -> None:
    lang = user.language
    text = await build_today_dashboard(session, user, lang=lang)
    kb = dashboard_kb(lang)
    if isinstance(target, CallbackQuery):
        await safe_edit_text(target.message, text, reply_markup=kb)
    elif edit:
        await safe_edit_text(target, text, reply_markup=kb)
    else:
        await deliver_long_text(target, text, reply_markup=kb)


async def show_projects(
    target: Message | CallbackQuery,
    user: User,
    session: AsyncSession,
    *,
    edit: bool = False,
) -> None:
    lang = user.language
    projects = await list_projects(session, user.id)
    active = await get_active_project(session, user)
    lines = [t(lang, "project_list_title")]
    if active:
        lines.append(t(lang, "project_active", title=active.title))
    for p in projects[:10]:
        mark = "📌 " if active and p.id == active.id else "• "
        lines.append(f"{mark}{p.title} ({p.project_type})")
    if not projects:
        lines.append("")
        lines.append(t(lang, "project_empty"))
    text = "\n".join(lines)
    kb = projects_kb(projects, active.id if active else None, lang)
    if isinstance(target, CallbackQuery):
        await safe_edit_text(target.message, text, reply_markup=kb)
    elif edit:
        await safe_edit_text(target, text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def show_workspace(
    target: Message | CallbackQuery,
    user: User,
    session: AsyncSession,
    *,
    edit: bool = False,
) -> None:
    lang = user.language
    docs = await list_workspace_documents(session, user, limit=15)
    lines = [t(lang, "workspace_list_title"), ""]
    if docs:
        for doc in docs:
            shared = " 👨‍👩‍👧" if doc.household_id else ""
            lines.append(f"• {doc.title} ({doc.char_count} chars){shared}")
    else:
        lines.append(t(lang, "workspace_empty"))
    lines.append("")
    lines.append(t(lang, "workspace_hint"))
    text = "\n".join(lines)
    kb = dashboard_kb(lang)
    if isinstance(target, CallbackQuery):
        await safe_edit_text(target.message, text, reply_markup=kb)
    elif edit:
        await safe_edit_text(target, text, reply_markup=kb)
    else:
        await deliver_long_text(target, text, reply_markup=kb)


async def run_export(message: Message, user: User, session: AsyncSession) -> None:
    from app.bot.quota_ui import answer_quota_block
    from app.services.export_service import build_user_export

    lang = user.language
    blocked = check_export_allowed(user, lang=lang)
    if blocked:
        await answer_quota_block(message, blocked, lang=lang)
        return
    include_vault = True
    if is_vault_protected(user) and not is_vault_unlocked(user):
        include_vault = False
    payload = await build_user_export(session, user.id, include_vault=include_vault)
    doc = BufferedInputFile(payload.encode("utf-8"), filename=f"life_ai_export_{user.telegram_id}.json")
    caption = t(lang, "export_done")
    if not include_vault:
        caption = f"{caption}\n\n{t(lang, 'export_vault_excluded')}"
    await message.answer_document(doc, caption=caption, reply_markup=back_menu_kb(lang))


async def create_project_from_title(
    message: Message,
    user: User,
    session: AsyncSession,
    title: str,
) -> None:
    lang = user.language
    project = await create_project(session, user, title=title.strip()[:255], description=title.strip()[:255])
    await message.answer(t(lang, "project_created", title=project.title), reply_markup=dashboard_kb(lang))


async def show_subscription(message: Message, user: User, session: AsyncSession) -> None:
    from app.bot.keyboards_subscription import subscription_kb
    from app.core.plans import TRIAL_DAYS

    await ensure_user_subscription_fields(session, user)
    lang = user.language
    await message.answer(
        t(lang, "sub_menu_intro", days=TRIAL_DAYS),
        reply_markup=subscription_kb(lang),
    )
