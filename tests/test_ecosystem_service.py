from datetime import datetime

from app.services.ecosystem_service import (
    UnifiedSearchResult,
    build_search_ai_context,
    format_unified_search,
    _next_credit_payment,
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


def test_next_credit_payment():
    from app.models.entities import CreditLoan

    loan = CreditLoan(payment_day=15, monthly_payment=500000, currency="UZS", title="Test")
    now = datetime(2026, 6, 20)
    due = _next_credit_payment(loan, now)
    assert due.month == 7
    assert due.day == 15
