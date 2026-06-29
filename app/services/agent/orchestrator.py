from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import User
from app.services.agent.planner import build_plan_llm, build_plan_rule_based
from app.services.agent.schemas import AgentPlan, AgentResult, AgentStep
from app.services.agent.tools import clear_agent_context, execute_tool, get_agent_context, set_agent_context
from app.services.ai_service import ask_ai
from app.services.dashboard_service import user_local_now
from app.services.personalization_service import agent_reply_prefix, personalization_system_note
from app.services.project_service import append_project_message, get_active_project, get_project_context

logger = logging.getLogger(__name__)


def plan_needs_confirm(plan: AgentPlan) -> bool:
    return any(step.requires_confirm for step in plan.steps)


def serialize_plan(plan: AgentPlan) -> dict:
    return {
        "intent": plan.intent,
        "reply_hint": plan.reply_hint,
        "steps": [
            {
                "tool": s.tool,
                "args": s.args,
                "requires_confirm": s.requires_confirm,
                "label": s.label,
            }
            for s in plan.steps
        ],
    }


def deserialize_plan(data: dict) -> AgentPlan:
    return AgentPlan(
        intent=data.get("intent") or "custom",
        reply_hint=data.get("reply_hint") or "",
        steps=[
            AgentStep(
                tool=s.get("tool", ""),
                args=s.get("args") or {},
                requires_confirm=bool(s.get("requires_confirm")),
                label=s.get("label") or "",
            )
            for s in data.get("steps") or []
            if s.get("tool")
        ],
    )


async def build_agent_plan(
    text: str,
    user: User,
    *,
    photo_context: dict[str, Any] | None = None,
) -> AgentPlan | None:
    now = user_local_now(user)
    plan = build_plan_rule_based(text, user_now=now)
    if plan:
        return plan
    if settings.openai_api_key.strip():
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        plan = await build_plan_llm(client, text, language=user.language)
        if plan:
            return plan
    if photo_context:
        steps = []
        if photo_context.get("analysis"):
            set_agent_context(user.id, document_text=photo_context["analysis"])
        amount = photo_context.get("amount")
        title = photo_context.get("title") or text[:120] or "Receipt"
        file_id = photo_context.get("file_id")
        if amount:
            steps.append(
                AgentStep(
                    "add_expense",
                    {"title": title, "amount": amount, "category": photo_context.get("category") or "shopping"},
                    requires_confirm=True,
                    label="expense",
                )
            )
        steps.append(
            AgentStep(
                "add_vault_record",
                {"title": title, "folder": photo_context.get("folder") or "receipts", "body": photo_context.get("analysis") or text, "file_id": file_id},
                requires_confirm=True,
                label="vault",
            )
        )
        if photo_context.get("warranty"):
            steps.append(
                AgentStep(
                    "add_vault_record",
                    {"title": f"Warranty: {title}", "folder": "warranty", "body": photo_context.get("analysis") or ""},
                    requires_confirm=True,
                    label="warranty",
                )
            )
        if photo_context.get("inventory"):
            steps.append(
                AgentStep("add_inventory", {"title": title, "location": "дом"}, requires_confirm=True, label="inventory")
            )
        return AgentPlan(intent="photo_receipt", steps=steps, reply_hint="finance")
    return None


async def execute_agent_plan(
    session: AsyncSession,
    user: User,
    plan: AgentPlan,
    *,
    bot=None,
    lang: str | None = None,
    skip_confirm: bool = False,
) -> AgentResult:
    lang = lang or user.language
    results = []
    files: list[tuple[bytes, str, str]] = []

    for step in plan.steps:
        if step.requires_confirm and not skip_confirm:
            continue
        result = await execute_tool(session, user, step.tool, step.args, bot=bot, lang=lang)
        results.append(result)

    ctx = get_agent_context(user.id)
    export_file = ctx.get("export_file")
    if export_file:
        files.append(export_file)
    chart = ctx.get("chart_png")
    if chart:
        files.append((chart, "chart.png", "image/png"))

    summary = await _compose_agent_reply(session, user, plan, results, lang=lang, bot=bot, user_message=text)
    project = await get_active_project(session, user)
    if project:
        await append_project_message(session, project.id, role="user", content=plan.intent)
        await append_project_message(session, project.id, role="assistant", content=summary[:4000])

    return AgentResult(text=summary, tool_results=results, files=files, used_ai=True)


async def run_agent(
    session: AsyncSession,
    user: User,
    text: str,
    *,
    bot=None,
    lang: str | None = None,
    photo_context: dict[str, Any] | None = None,
    auto_confirm: bool = False,
) -> AgentResult:
    lang = lang or user.language
    clear_agent_context(user.id)
    set_agent_context(user.id, user_message=text)
    if photo_context:
        set_agent_context(user.id, **{k: v for k, v in photo_context.items() if v is not None})

    plan = await build_agent_plan(text, user, photo_context=photo_context)
    if not plan:
        answer = await ask_ai(
            user_message=text,
            module_hint=personalization_system_note(user),
            language=lang,
            session=session,
            user=user,
            bot=bot,
            usage_source="agent_fallback",
        )
        return AgentResult(text=answer, used_ai=True)

    if plan_needs_confirm(plan) and not auto_confirm:
        preview = _format_plan_preview(plan, lang)
        return AgentResult(text=preview, pending=True, plan=plan)

    return await execute_agent_plan(session, user, plan, bot=bot, lang=lang, skip_confirm=auto_confirm)


def _format_plan_preview(plan: AgentPlan, lang: str) -> str:
    from app.core.i18n import t

    lines = [t(lang, "agent_confirm_title"), ""]
    for idx, step in enumerate(plan.steps, 1):
        if not step.requires_confirm:
            continue
        label = step.label or step.tool
        detail = json.dumps(step.args, ensure_ascii=False)[:120]
        lines.append(f"{idx}. {label}: {detail}")
    lines.append("")
    lines.append(t(lang, "agent_confirm_hint"))
    return "\n".join(lines)


async def _compose_agent_reply(session, user, plan, results, *, lang, bot, user_message: str = "") -> str:
    from app.core.i18n import t
    from app.core.modules.ui_texts import module_hint_text

    prefix = agent_reply_prefix(user, lang)
    ctx = get_agent_context(user.id)
    user_message = user_message or str(ctx.get("user_message") or ctx.get("last_query") or "")

    web_empty = any(
        res.ok and res.tool == "web_research" and not (res.data or {}).get("context")
        for res in results
    )
    research_done = any(res.ok and res.tool == "research_report" for res in results)

    if web_empty and user_message and not research_done and settings.openai_api_key.strip():
        module_id = "business" if "business" in (plan.intent or "") else "ai_assistant"
        hint = module_hint_text(module_id, lang) + "\n" + personalization_system_note(user)
        answer = await ask_ai(
            user_message=user_message,
            module_hint=hint,
            language=lang,
            session=session,
            user=user,
            bot=bot,
            max_completion_tokens=2500,
            module_id=module_id,
            usage_source="agent_web_fallback",
        )
        if answer and not answer.startswith("⚠️"):
            return f"{prefix}\n\n{answer}"

    done_lines = [prefix, ""]
    failed = []
    for res in results:
        if res.ok:
            if res.tool in {"search_data", "analyze_spending", "web_research", "research_report", "explain_document", "teacher_session", "trainer_session"}:
                done_lines.append(res.message)
            else:
                done_lines.append(f"✅ {res.message}")
        else:
            failed.append(res.message)

    if not results:
        done_lines.append(t(lang, "agent_nothing_executed"))
    if failed:
        done_lines.append(t(lang, "agent_errors"))
        done_lines.extend(f"⚠️ {e}" for e in failed[:3])

    project = await get_active_project(session, user)
    project_ctx = await get_project_context(session, project.id) if project else ""
    if plan.reply_hint in {"shopping", "travel", "finance", "business"} and results and settings.openai_api_key.strip():
        ctx = get_agent_context(user.id)
        extra = await ask_ai(
            user_message=(
                f"Summarize completed actions for user in {lang}. Intent: {plan.intent}. "
                f"Results: {[r.message[:200] for r in results if r.ok]}"
            ),
            module_hint=personalization_system_note(user) + (f"\n{project_ctx[:1500]}" if project_ctx else ""),
            language=lang,
            session=session,
            user=user,
            bot=bot,
            max_completion_tokens=800,
            usage_source="agent_summary",
        )
        if extra and not extra.startswith("⚠️"):
            done_lines.extend(["", extra[:1500]])

    return "\n".join(done_lines).strip()
