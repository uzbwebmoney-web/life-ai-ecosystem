from __future__ import annotations

import pytest

from app.services.agent.planner import build_plan_rule_based
from app.services.unified_ai.file_router import classify_upload
from app.services.unified_ai.intent_router import analyze_intent
from app.services.unified_ai.suggestions import should_offer_save, smart_suggestions


def test_intent_fridge_purchase_modules():
    intent = analyze_intent("Я купил холодильник.")
    assert "finance" in intent.modules or "home" in intent.modules
    assert intent.goal == "purchase"
    assert intent.needs_agent


def test_intent_travel_turkey():
    intent = analyze_intent("Я еду в Турцию.")
    assert "travel" in intent.modules
    assert intent.goal == "travel_prep"
    assert "organizer" in intent.modules or "finance" in intent.modules


def test_intent_car_reminder():
    intent = analyze_intent("Напомни заменить масло через 5000 км.")
    assert "car" in intent.modules
    assert "reminder" in intent.action_types


def test_planner_appliance_purchase():
    plan = build_plan_rule_based("Я купил холодильник за 5 млн сум.")
    assert plan is not None
    tools = {s.tool for s in plan.steps}
    assert "add_inventory" in tools
    assert "add_expense" in tools


def test_planner_travel_turkey():
    plan = build_plan_rule_based("Я еду в Турцию через 14 дней.")
    assert plan is not None
    assert plan.intent == "travel_prep"
    tools = {s.tool for s in plan.steps}
    assert "web_research" in tools
    assert "add_calendar_event" in tools
    assert "add_task" in tools


def test_file_router_receipt():
    cls = classify_upload("Receipt total 150000 UZS", caption="чек магазин")
    assert cls.doc_type == "receipt"
    assert "finance" in cls.related_modules
    assert "vault" in cls.related_modules


def test_smart_suggestions_back_pain():
    intent = analyze_intent("Болит спина.")
    actions = smart_suggestions(intent, "Болит спина.", "Отдых и лёгкая растяжка.", "ru")
    ids = {a.action_id for a in actions}
    assert "symptom_diary" in ids or "med_remind" in ids


def test_should_offer_save_health():
    intent = analyze_intent("Болит спина уже 3 дня.")
    assert should_offer_save(intent, "Болит спина.", "A" * 100, memory_enabled=True)
