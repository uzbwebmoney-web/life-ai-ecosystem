from app.services.business_service import BUSINESS_SUBMODULE_AI, business_submodule_description
from app.services.module_context import build_module_ai_hint


def test_business_submodule_description():
    desc = business_submodule_description("plans", "ru")
    assert "бизнес" in desc.lower() or "план" in desc.lower()


def test_business_ai_hints():
    assert "consultant" in BUSINESS_SUBMODULE_AI
    assert "sales_analysis" in BUSINESS_SUBMODULE_AI
    assert len(BUSINESS_SUBMODULE_AI) == 7


def test_module_hint_scoped_to_business():
    hint = build_module_ai_hint("business", "contracts", lang="ru")
    assert "Бизнес" in hint
    assert "договор" in hint.lower() or "юрист" in hint.lower()
