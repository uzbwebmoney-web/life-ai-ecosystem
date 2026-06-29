from app.services.agent.intent import detect_special_mode, should_route_to_agent
from app.services.agent.planner import build_plan_rule_based, _extract_amount
from app.services.table_export_service import build_table_bytes, extract_table_from_text


def test_should_route_to_agent_reminder():
    assert should_route_to_agent("Напомни мне заменить масло через 5000 км")


def test_should_route_to_agent_search():
    assert should_route_to_agent("Где мой паспорт?")


def test_should_route_to_agent_photo():
    assert should_route_to_agent("", has_photo=True)


def test_build_plan_reminder():
    plan = build_plan_rule_based("Напомни заменить масло через 5000 км")
    assert plan is not None
    assert plan.intent == "car_oil"
    assert len(plan.steps) >= 1


def test_build_plan_search():
    plan = build_plan_rule_based("Где мой паспорт?")
    assert plan is not None
    assert plan.steps[0].tool == "search_data"


def test_build_plan_travel():
    plan = build_plan_rule_based("Я еду в Турцию через неделю")
    assert plan is not None
    assert plan.intent == "travel_prep"


def test_build_plan_research():
    plan = build_plan_rule_based("Исследование на тему AI agents")
    assert plan is not None
    assert plan.intent == "research"


def test_extract_amount_million():
    assert _extract_amount("купил холодильник за 8 млн") == 8_000_000


def test_table_export_csv():
    rows = [["Name", "Price"], ["A", "100"]]
    data, name, mime = build_table_bytes(rows, fmt="csv", title="test")
    assert name.endswith(".csv")
    assert b"Name" in data


def test_extract_table_from_markdown():
    text = "| Model | Price |\n| --- | --- |\n| X | 800 |"
    rows = extract_table_from_text(text)
    assert len(rows) >= 2
