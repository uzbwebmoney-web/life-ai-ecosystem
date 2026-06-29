from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.agent.schemas import ToolRunResult
from app.services.analytics_service import analyze_spending_period, format_spending_analysis
from app.services.dashboard_service import user_local_now
from app.services.document_explain_service import explain_document_text
from app.services.ecosystem_service import format_unified_search, unified_search
from app.services.finance_service import add_finance_transaction
from app.services.home_service import add_inventory_item
from app.services.life_data import add_record, add_reminder
from app.services.household_calendar_service import add_household_event
from app.services.project_service import append_project_message, create_project, get_active_project
from app.services.research_service import build_research_report
from app.services.table_export_service import build_table_bytes, extract_table_from_text
from app.services.teacher_service import run_teacher_turn
from app.services.trainer_service import run_trainer_turn
from app.services.car_service import add_car_maintenance
from app.services.organizer_service import add_task
from app.services.web_search_service import fetch_web_context
from app.services.workspace_rag_service import build_workspace_rag_context

logger = logging.getLogger(__name__)

_context_store: dict[int, dict[str, Any]] = {}


def set_agent_context(user_id: int, **kwargs: Any) -> None:
    _context_store[user_id] = {**_context_store.get(user_id, {}), **kwargs}


def get_agent_context(user_id: int) -> dict[str, Any]:
    return dict(_context_store.get(user_id, {}))


def clear_agent_context(user_id: int) -> None:
    _context_store.pop(user_id, None)


async def execute_tool(
    session: AsyncSession,
    user: User,
    tool: str,
    args: dict[str, Any],
    *,
    bot=None,
    lang: str = "ru",
) -> ToolRunResult:
    try:
        if tool == "search_data":
            return await _tool_search_data(session, user, args, lang=lang)
        if tool == "add_expense":
            return await _tool_add_expense(session, user, args, lang=lang)
        if tool == "add_reminder":
            return await _tool_add_reminder(session, user, args, lang=lang)
        if tool == "add_task":
            return await _tool_add_task(session, user, args, lang=lang)
        if tool == "add_vault_record":
            return await _tool_add_vault(session, user, args, lang=lang)
        if tool == "add_inventory":
            return await _tool_add_inventory(session, user, args, lang=lang)
        if tool == "add_car_maintenance":
            return await _tool_add_car_maintenance(session, user, args, lang=lang)
        if tool == "add_calendar_event":
            return await _tool_add_calendar(session, user, args, lang=lang)
        if tool == "web_research":
            return await _tool_web_research(user, args, lang=lang)
        if tool == "analyze_spending":
            return await _tool_analyze_spending(session, user, args, lang=lang)
        if tool == "generate_chart":
            return await _tool_generate_chart(session, user, args, lang=lang)
        if tool == "explain_document":
            return await _tool_explain_document(session, user, args, bot=bot, lang=lang)
        if tool == "create_project":
            return await _tool_create_project(session, user, args, lang=lang)
        if tool == "research_report":
            return await _tool_research_report(session, user, args, bot=bot, lang=lang)
        if tool == "export_comparison_table":
            return await _tool_export_table(user, args, lang=lang)
        if tool == "export_from_context":
            return await _tool_export_from_context(user, args, lang=lang)
        if tool == "teacher_session":
            return await _tool_teacher(session, user, args, bot=bot, lang=lang)
        if tool == "trainer_session":
            return await _tool_trainer(session, user, args, bot=bot, lang=lang)
        if tool == "create_presentation":
            return await _tool_create_presentation(user, args, lang=lang)
        return ToolRunResult(tool, False, f"Unknown tool: {tool}")
    except Exception as exc:
        logger.exception("Tool %s failed", tool)
        return ToolRunResult(tool, False, str(exc))


async def _tool_search_data(session, user, args, *, lang) -> ToolRunResult:
    query = str(args.get("query") or "").strip()
    if not query:
        return ToolRunResult("search_data", False, "Empty query")
    results = await unified_search(session, user, query, limit=int(args.get("limit") or 8))
    lines = format_unified_search(results, lang, query)
    rag = await build_workspace_rag_context(session, user, query, limit=3)
    if rag and len(lines) <= 2:
        lines.append(rag)
    elif rag:
        lines.append(f"\n{rag}")
    if len(lines) <= 1:
        return ToolRunResult("search_data", True, "Nothing found", {"lines": lines})
    return ToolRunResult("search_data", True, "\n".join(lines), {"lines": lines, "results": results})


async def _tool_add_expense(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Расход")[:255]
    amount = float(args.get("amount") or 0)
    if amount <= 0:
        return ToolRunResult("add_expense", False, "Invalid amount")
    category = str(args.get("category") or "other")
    rec = await add_finance_transaction(
        session,
        user_id=user.id,
        tx_type="expense",
        title=title,
        amount=amount,
        category=category,
        profile_id=user.active_profile_id,
    )
    return ToolRunResult(
        "add_expense",
        True,
        f"Expense saved: {title} — {amount:,.0f} UZS",
        {"record_id": rec.id},
    )


async def _tool_add_reminder(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Reminder")[:255]
    days = int(args.get("days_ahead") or 0)
    due = user_local_now(user) + timedelta(days=days)
    if due.hour < 8:
        due = due.replace(hour=9, minute=0, second=0, microsecond=0)
    module_id = str(args.get("module_id") or "organizer")
    notes = str(args.get("notes") or "")
    if notes:
        title = f"{title} ({notes})"
    rem = await add_reminder(
        session,
        user_id=user.id,
        title=title[:255],
        due_at=due,
        module_id=module_id,
        profile_id=user.active_profile_id,
        user=user,
        lang=lang,
    )
    if not rem:
        return ToolRunResult("add_reminder", False, "Reminder limit reached")
    return ToolRunResult("add_reminder", True, f"Reminder: {title} — {due.strftime('%d.%m.%Y %H:%M')}", {"id": rem.id})


async def _tool_add_task(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Task")[:255]
    task = await add_task(session, user_id=user.id, title=title, profile_id=user.active_profile_id)
    return ToolRunResult("add_task", True, f"Task added: {title}", {"id": task.id})


async def _tool_add_vault(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Document")[:255]
    body = str(args.get("body") or title)
    folder = str(args.get("folder") or "documents")
    file_id = args.get("file_id")
    if file_id:
        body = f"file_id={file_id}\n\n{body}"
    rec = await add_record(
        session,
        user_id=user.id,
        module_id="vault",
        submodule_id=folder if folder in {"documents", "passport", "policies", "warranty", "receipts", "notes"} else "documents",
        title=title,
        body=body,
        profile_id=user.active_profile_id,
    )
    return ToolRunResult("add_vault_record", True, f"Saved to vault: {title}", {"record_id": rec.id})


async def _tool_add_inventory(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Item")[:255]
    location = str(args.get("location") or "")
    item = await add_inventory_item(
        session,
        user_id=user.id,
        title=title,
        location=location,
        profile_id=user.active_profile_id,
    )
    return ToolRunResult("add_inventory", True, f"Inventory: {title}", {"id": item.id})


async def _tool_add_car_maintenance(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Maintenance")[:255]
    notes = str(args.get("notes") or "")
    due = user_local_now(user) + timedelta(days=int(args.get("days_ahead") or 90))
    item = await add_car_maintenance(
        session,
        user_id=user.id,
        item_type=str(args.get("item_type") or "oil"),
        title=title,
        due_at=due,
        notes=notes,
        profile_id=user.active_profile_id,
    )
    return ToolRunResult("add_car_maintenance", True, f"Car maintenance: {title}", {"id": item.id})


async def _tool_add_calendar(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Event")[:255]
    days = int(args.get("days_ahead") or 0)
    starts = user_local_now(user) + timedelta(days=days)
    event_type = str(args.get("event_type") or "meeting")
    ev = await add_household_event(
        session,
        user,
        title=title,
        starts_at=starts,
        event_type=event_type,
        profile_id=user.active_profile_id,
    )
    return ToolRunResult("add_calendar_event", True, f"Calendar: {title} — {starts.strftime('%d.%m.%Y')}", {"id": ev.id})


async def _tool_web_research(user, args, *, lang) -> ToolRunResult:
    from app.core.i18n import t

    query = str(args.get("query") or "")
    ctx, links = await fetch_web_context(query, language=lang, max_results=12)
    set_agent_context(user.id, web_context=ctx, web_links=links, last_query=query)
    if ctx:
        preview = ctx[:2000]
    else:
        preview = t(lang, "agent_no_web_results")
    return ToolRunResult("web_research", True, preview, {"context": ctx, "links": links, "empty": not ctx})


async def _tool_analyze_spending(session, user, args, *, lang) -> ToolRunResult:
    days = int(args.get("period_days") or 30)
    data = await analyze_spending_period(session, user, days=days)
    text = format_spending_analysis(data, lang=lang)
    set_agent_context(user.id, spending_analysis=data)
    return ToolRunResult("analyze_spending", True, text, {"analysis": data})


async def _tool_generate_chart(session, user, args, *, lang) -> ToolRunResult:
    from app.services.analytics_service import build_expense_chart_png

    ctx = get_agent_context(user.id)
    analysis = ctx.get("spending_analysis")
    if not analysis:
        return ToolRunResult("generate_chart", False, "No analysis data")
    png = build_expense_chart_png(analysis)
    if not png:
        return ToolRunResult("generate_chart", False, "Chart failed")
    set_agent_context(user.id, chart_png=png)
    return ToolRunResult("generate_chart", True, "Chart generated", {"png": png})


async def _tool_explain_document(session, user, args, *, bot, lang) -> ToolRunResult:
    text = str(args.get("text") or "")
    ctx = get_agent_context(user.id)
    if not text and ctx.get("document_text"):
        text = ctx["document_text"]
    if not text:
        return ToolRunResult("explain_document", False, "No document text")
    answer = await explain_document_text(
        session,
        user,
        text,
        risk_check=bool(args.get("risk_check")),
        bot=bot,
        lang=lang,
    )
    return ToolRunResult("explain_document", True, answer)


async def _tool_create_project(session, user, args, *, lang) -> ToolRunResult:
    title = str(args.get("title") or "Project")[:255]
    desc = str(args.get("description") or "")
    ptype = str(args.get("project_type") or "general")
    project = await create_project(session, user, title=title, description=desc, project_type=ptype)
    return ToolRunResult("create_project", True, f"Project created: {title}", {"project_id": project.id})


async def _tool_research_report(session, user, args, *, bot, lang) -> ToolRunResult:
    topic = str(args.get("topic") or "")
    report = await build_research_report(session, user, topic, bot=bot, lang=lang, depth=str(args.get("depth") or "standard"))
    set_agent_context(user.id, research_report=report)
    return ToolRunResult("research_report", True, report[:3500], {"full_report": report})


async def _tool_export_table(user, args, *, lang) -> ToolRunResult:
    fmt = str(args.get("format") or "csv")
    ctx = get_agent_context(user.id)
    content = ctx.get("web_context") or ctx.get("research_report") or str(args.get("content") or "")
    rows = extract_table_from_text(content)
    if not rows:
        rows = [["Item", "Info"], ["Query", ctx.get("last_query") or "—"], ["Results", content[:200]]]
    data, filename, mime = build_table_bytes(rows, fmt=fmt, title="Comparison")
    set_agent_context(user.id, export_file=(data, filename, mime))
    return ToolRunResult("export_from_context", True, f"Table ready: {filename}", {"file": (data, filename, mime)})


async def _tool_export_from_context(user, args, *, lang) -> ToolRunResult:
    args = {**args, "format": args.get("format") or "csv"}
    return await _tool_export_table(user, args, lang=lang)


async def _tool_teacher(session, user, args, *, bot, lang) -> ToolRunResult:
    topic = str(args.get("topic") or "")
    answer = await run_teacher_turn(session, user, topic, bot=bot, lang=lang)
    return ToolRunResult("teacher_session", True, answer)


async def _tool_trainer(session, user, args, *, bot, lang) -> ToolRunResult:
    msg = str(args.get("message") or "")
    answer = await run_trainer_turn(session, user, msg, bot=bot, lang=lang)
    return ToolRunResult("trainer_session", True, answer)


async def _tool_create_presentation(user, args, *, lang) -> ToolRunResult:
    from app.services.table_export_service import build_presentation_bytes, slides_from_text

    title = str(args.get("title") or "Presentation")[:200]
    content = str(args.get("content") or "")
    ctx = get_agent_context(user.id)
    if not content:
        content = ctx.get("research_report") or ctx.get("web_context") or ""
    fmt = "pptx" if str(args.get("format") or "pptx").lower() != "docx" else "docx"
    slides = slides_from_text(content, default_title=title)
    if not slides:
        slides = [(title, content[:2000])]
    data, filename = build_presentation_bytes(title, slides, fmt=fmt)  # type: ignore[arg-type]
    set_agent_context(user.id, export_file=(data, filename, "application/vnd.openxmlformats-officedocument.presentationml.presentation"))
    return ToolRunResult("create_presentation", True, f"Presentation: {filename}", {"file": (data, filename, "")})
