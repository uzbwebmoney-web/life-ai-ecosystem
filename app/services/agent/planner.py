from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from app.services.agent.schemas import AgentPlan, AgentStep
from app.services.agent.intent import detect_special_mode
from app.services.dashboard_service import user_local_now


def _extract_amount(text: str) -> float | None:
    mln_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:млн|mln|million)", text, re.I)
    if mln_match:
        try:
            return float(mln_match.group(1).replace(",", ".")) * 1_000_000
        except ValueError:
            pass
    patterns = (
        r"(\d[\d\s.,]{2,})\s*(?:сум|so'm|uzs|₽|rub|\$|usd|млн|million|mln)",
        r"(?:за|for|narxi)\s*(\d[\d\s.,]{2,})",
        r"(\d[\d\s.,]{4,})",
    )
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if not m:
            continue
        raw = m.group(1).replace(" ", "").replace(",", ".")
        try:
            val = float(raw)
            if "млн" in text.lower() or "million" in text.lower() or "mln" in text.lower():
                if val < 1000:
                    val *= 1_000_000
            return val if val > 0 else None
        except ValueError:
            continue
    return None


def _extract_km(text: str) -> int | None:
    m = re.search(r"(\d{3,6})\s*(?:км|km)", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"через\s+(\d{3,6})", text, re.I)
    return int(m.group(1)) if m else None


def _extract_days(text: str) -> int | None:
    m = re.search(r"через\s+(\d{1,3})\s*(?:дн|day|kun)", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,3})\s*(?:дн|day|kun)\s*(?:через|keyin|later)", text, re.I)
    return int(m.group(1)) if m else None


def _extract_title_from_reminder(text: str) -> str:
    cleaned = re.sub(
        r"^(?:напомни(?:\s+мне)?|remind me|eslat(?:ma)?)\s+(?:что|that|to|ga|ni)?\s*",
        "",
        text,
        flags=re.I,
    ).strip()
    return cleaned[:200] or text[:200]


def _search_query(text: str) -> str:
    for pat in (
        r"(?:где|qayerda|where(?:\s+is)?)\s+(?:мой|my|mening)?\s*(.+?)[?.!]?$",
        r"(?:когда|qachon|when)\s+(?:я|I|men)?\s*(.+?)[?.!]?$",
        r"(?:покажи|show|ko'rsat)\s+(.+?)[?.!]?$",
        r"(?:найди|find|top)\s+(.+?)[?.!]?$",
    ):
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1).strip()[:120]
    return text[:120]


def build_plan_rule_based(text: str, *, user_now: datetime | None = None) -> AgentPlan | None:
    t = (text or "").strip()
    low = t.lower()
    now = user_now or datetime.utcnow()
    special = detect_special_mode(t)

    if special == "research":
        topic = re.sub(r"^(?:исследован|research|отч[её]т|report)\s*(?:на тему|about|mavzu)?\s*", "", t, flags=re.I).strip()
        return AgentPlan(
            intent="research",
            steps=[AgentStep("research_report", {"topic": topic or t, "depth": "deep"})],
            reply_hint="research",
        )

    if special == "teacher":
        topic = re.sub(r"режим преподав|teacher mode|o'qituvchi rejimi", "", t, flags=re.I).strip()
        return AgentPlan(
            intent="teacher",
            steps=[AgentStep("teacher_session", {"topic": topic or t})],
            reply_hint="teacher",
        )

    if special == "trainer":
        return AgentPlan(intent="trainer", steps=[AgentStep("trainer_session", {"message": t})], reply_hint="trainer")

    if re.search(r"создай проект|новый проект|create project|yangi loyiha", low):
        title = re.sub(r".*?(?:проект|project|loyiha)\s*", "", t, flags=re.I).strip(" :\"'«»")
        return AgentPlan(
            intent="create_project",
            steps=[
                AgentStep(
                    "create_project",
                    {"title": title or "Новый проект", "description": t},
                    requires_confirm=False,
                )
            ],
        )

    if re.search(r"бизнес|business|biznes|стартап|startup", low) and re.search(
        r"иде[яи]|idea|g'oya|goya|loyiha|нужен|kerak|need|подскаж|совет|maslahat|tavsiya",
        low,
    ):
        return AgentPlan(
            intent="business_ideas",
            steps=[AgentStep("research_report", {"topic": t, "depth": "standard"})],
            reply_hint="business",
        )

    if re.search(r"найди|compare|сравни|solishtir|best|лучш|дешев", low) and re.search(
        r"ноутбук|laptop|телефон|phone|товар|product|модел|model|билет|ticket|flight",
        low,
    ):
        export_fmt = "xlsx" if re.search(r"excel|xlsx|таблиц", low) else "csv"
        return AgentPlan(
            intent="product_research",
            steps=[
                AgentStep("web_research", {"query": t, "compare": True}),
                AgentStep("export_comparison_table", {"format": export_fmt}),
            ],
            reply_hint="shopping",
        )

    if re.search(r"презентац|presentation|powerpoint|pptx|slides", low):
        return AgentPlan(
            intent="presentation",
            steps=[AgentStep("create_presentation", {"title": t[:120], "content": t, "format": "pptx"})],
        )

    if re.search(r"сделай таблиц|make table|jadval|excel|csv", low):
        return AgentPlan(
            intent="export_table",
            steps=[AgentStep("export_from_context", {"format": "xlsx" if "excel" in low else "csv", "content": t})],
        )

    if re.search(r"анализ (?:расход|трат|истори)|spending analysis|xarajat tahlili", low):
        return AgentPlan(
            intent="spending_analysis",
            steps=[AgentStep("analyze_spending", {"period_days": 30}), AgentStep("generate_chart", {"chart_type": "expenses"})],
        )

    if re.search(r"объясни (?:договор|контракт|document)|explain (?:contract|document)", low):
        doc = re.sub(r".*?(?:договор|контракт|document)\s*", "", t, flags=re.I).strip()
        return AgentPlan(
            intent="explain_document",
            steps=[AgentStep("explain_document", {"text": doc or t, "risk_check": True})],
        )

    if re.search(r"еду в|leaving for|sayohat|поездк|trip to|через \d+ (?:дн|day|kun)|turkey|турци", low):
        country = ""
        m = re.search(r"(?:в|to|ga)\s+([A-Za-zА-Яа-яЁё\-]+)", t)
        if m:
            country = m.group(1)
        if not country and re.search(r"turkey|турци|istanbul|стамбул", low):
            country = "Turkey"
        days = _extract_days(t) or 7
        return AgentPlan(
            intent="travel_prep",
            steps=[
                AgentStep("search_data", {"query": "паспорт passport", "limit": 3}),
                AgentStep("web_research", {"query": f"{country or t} visa requirements passport Uzbekistan", "compare": False}),
                AgentStep("web_research", {"query": f"{country or t} travel budget estimate packing checklist", "compare": False}),
                AgentStep(
                    "add_calendar_event",
                    {
                        "title": f"Поездка: {country or 'travel'}",
                        "days_ahead": days,
                        "event_type": "travel",
                    },
                    requires_confirm=True,
                    label="calendar",
                ),
                AgentStep(
                    "add_task",
                    {"title": f"Собрать вещи: {country or 'поездка'}", "notes": "Чек-лист из AI-ответа"},
                    requires_confirm=True,
                    label="checklist",
                ),
            ],
            reply_hint="travel",
        )

    if re.search(r"(?:купил|купила|bought|приобрел)\s", low) and re.search(
        r"холодильник|fridge|стирал|washer|техник|appliance|микровол|oven|плит",
        low,
    ):
        title = re.sub(r"^(?:я\s+)?(?:купил|купила|bought|приобрел)\s+", "", t, flags=re.I).strip()[:200]
        amount = _extract_amount(t)
        steps = [
            AgentStep(
                "add_inventory",
                {"title": title or "Техника", "location": "дом"},
                requires_confirm=True,
                label="inventory",
            ),
            AgentStep(
                "add_vault_record",
                {"title": f"Гарантия: {title or 'техника'}", "folder": "warranty", "body": t},
                requires_confirm=True,
                label="warranty",
            ),
        ]
        if amount:
            steps.insert(
                0,
                AgentStep(
                    "add_expense",
                    {"title": title or "Покупка техники", "amount": amount, "category": "home"},
                    requires_confirm=True,
                    label="expense",
                ),
            )
        else:
            steps.append(
                AgentStep(
                    "add_vault_record",
                    {"title": f"Чек: {title or 'покупка'}", "folder": "receipts", "body": t},
                    requires_confirm=True,
                    label="receipt",
                )
            )
        return AgentPlan(intent="appliance_purchase", steps=steps, reply_hint="finance")

    if re.search(r"замени масло|change oil|yog'|масл.*\d{3,}\s*км", low):
        km = _extract_km(t) or 5000
        return AgentPlan(
            intent="car_oil",
            steps=[
                AgentStep(
                    "add_car_maintenance",
                    {"title": "Замена масла", "notes": f"Через {km} км"},
                    requires_confirm=True,
                    label="car",
                ),
                AgentStep(
                    "add_reminder",
                    {"title": f"Замена масла (~{km} км)", "days_ahead": 90, "module_id": "car"},
                    requires_confirm=True,
                    label="reminder",
                ),
            ],
        )

    if re.search(r"напомни|remind|eslat", low):
        title = _extract_title_from_reminder(t)
        km = _extract_km(t)
        module = "car" if km or re.search(r"масл|oil|то\b|service", low) else "organizer"
        args: dict = {"title": title, "days_ahead": 0, "module_id": module}
        if km:
            args["notes"] = f"Через {km} км"
        return AgentPlan(
            intent="reminder",
            steps=[AgentStep("add_reminder", args, requires_confirm=True, label="reminder")],
        )

    if re.search(r"где|qayerda|where|когда|qachon|when|покажи чек|show receipt", low):
        return AgentPlan(
            intent="search",
            steps=[AgentStep("search_data", {"query": _search_query(t), "limit": 8})],
        )

    if re.search(r"запиши расход|add expense|xarajat|купил|bought|потратил|spent", low):
        amount = _extract_amount(t)
        title = re.sub(r"^(?:запиши|add|купил|bought|потратил)\s*", "", t, flags=re.I).strip()[:200]
        category = "home" if re.search(r"холодильник|fridge|дом|home|uy", low) else "shopping"
        steps = []
        if amount:
            steps.append(
                AgentStep(
                    "add_expense",
                    {"title": title or "Расход", "amount": amount, "category": category},
                    requires_confirm=True,
                    label="expense",
                )
            )
        if re.search(r"инвентар|inventory|холодильник|fridge|техник", low):
            steps.append(
                AgentStep(
                    "add_inventory",
                    {"title": title or "Покупка", "location": "дом"},
                    requires_confirm=True,
                    label="inventory",
                )
            )
        if re.search(r"гарант|warranty|kafolat|чек|receipt", low):
            steps.append(
                AgentStep(
                    "add_vault_record",
                    {"title": title or "Чек", "folder": "warranty", "body": t},
                    requires_confirm=True,
                    label="vault",
                )
            )
        if steps:
            return AgentPlan(intent="purchase_record", steps=steps, reply_hint="finance")
        return None

    if re.search(r"сохрани|save|saqlang", low):
        folder = "receipts"
        if re.search(r"гарант|warranty", low):
            folder = "warranty"
        elif re.search(r"авто|car|mashina", low):
            folder = "car"
        amount = _extract_amount(t)
        steps = [
            AgentStep(
                "add_vault_record",
                {"title": t[:120], "folder": folder, "body": t},
                requires_confirm=True,
                label="vault",
            )
        ]
        if amount:
            steps.insert(
                0,
                AgentStep(
                    "add_expense",
                    {"title": t[:120], "amount": amount, "category": "shopping"},
                    requires_confirm=True,
                    label="expense",
                ),
            )
        return AgentPlan(intent="save", steps=steps)

    return None


async def build_plan_llm(client, text: str, *, language: str = "ru") -> AgentPlan | None:
    if not client:
        return None
    prompt = (
        "You are a task planner. Return ONLY valid JSON with keys: intent, steps (array of {tool, args, requires_confirm, label}). "
        "Available tools: search_data, add_expense, add_reminder, add_task, add_vault_record, add_inventory, "
        "add_car_maintenance, add_calendar_event, web_research, analyze_spending, explain_document, create_project, research_report. "
        f"User message: {text[:500]}"
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return compact JSON only."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.2,
        )
        raw = (response.choices[0].message.content or "").strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw)
        data = json.loads(raw)
        steps = [
            AgentStep(
                tool=s.get("tool", ""),
                args=s.get("args") or {},
                requires_confirm=bool(s.get("requires_confirm", True)),
                label=s.get("label") or s.get("tool", ""),
            )
            for s in data.get("steps") or []
            if s.get("tool")
        ]
        if not steps:
            return None
        return AgentPlan(intent=data.get("intent") or "custom", steps=steps)
    except Exception:
        return None
