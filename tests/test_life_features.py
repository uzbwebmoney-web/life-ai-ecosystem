from app.services.life_profile_service import parse_remember_text
from app.services.scanner_service import classify_scan, parse_amount_from_text


def test_parse_remember_ru():
    assert parse_remember_text("Запомни: аллергия на пенициллин") == "аллергия на пенициллин"


def test_parse_remember_en():
    assert parse_remember_text("Remember: I drive a Tesla") == "I drive a Tesla"


def test_classify_scan_receipt():
    mod, sub, folder = classify_scan("Receipt total 150000 UZS grocery store")
    assert folder == "receipts"


def test_classify_scan_health():
    mod, sub, folder = classify_scan("Blood test results hemoglobin")
    assert mod == "health"


def test_parse_amount():
    assert parse_amount_from_text("Total 150000 UZS") == 150000.0
