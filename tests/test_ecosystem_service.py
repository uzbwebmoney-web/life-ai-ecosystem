
from app.services.ecosystem_service import (
    UnifiedSearchResult,
    build_search_ai_context,
    format_unified_search,
)


def test_build_search_ai_context():
    from app.models.entities import LifeRecord, MemoryEntry

    results = UnifiedSearchResult(
        records=[LifeRecord(module_id="car", title="Oil change", body="2026-03-15")],
        memory=[MemoryEntry(content="Toyota Camry 2018")],
    )
    ctx = build_search_ai_context(results)
    assert "Oil change" in ctx
    assert "Toyota" in ctx


def test_format_unified_search_empty():
    lines = format_unified_search(UnifiedSearchResult(), "ru", "масло")
    text = "\n".join(lines)
    assert "масло" in text
    assert "Ничего" in text or "topilmadi" in text.lower() or "Nothing" in text
