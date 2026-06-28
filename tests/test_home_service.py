from app.services.home_service import HOME_SUBMODULE_AI, STATUS_CYCLE, parse_amount


def test_home_ai_hints():
    assert "repair" in HOME_SUBMODULE_AI
    assert len(HOME_SUBMODULE_AI) == 1


def test_repair_status_cycle():
    assert STATUS_CYCLE["planned"] == "in_progress"
    assert STATUS_CYCLE["done"] == "planned"


def test_parse_amount():
    assert parse_amount("50000") == 50000.0
    assert parse_amount("0") is None
