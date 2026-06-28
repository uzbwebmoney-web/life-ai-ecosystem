from app.services.travel_service import TRAVEL_SUBMODULE_AI, convert_currency, parse_amount, travel_submodule_description


def test_travel_submodule_description():
    desc = travel_submodule_description("packing", "ru")
    assert "чек" in desc.lower() or "вещ" in desc.lower() or "спис" in desc.lower()


def test_travel_ai_hints():
    assert "routes" in TRAVEL_SUBMODULE_AI
    assert "currency" in TRAVEL_SUBMODULE_AI
    assert len(TRAVEL_SUBMODULE_AI) == 6


def test_convert_currency_usd_to_uzs():
    result = convert_currency(100, "USD", "UZS")
    assert result is not None
    assert result == 100 * 12_600


def test_convert_currency_same():
    result = convert_currency(50, "EUR", "EUR")
    assert result == 50


def test_parse_amount():
    assert parse_amount("1 500") == 1500.0
    assert parse_amount("abc") is None
