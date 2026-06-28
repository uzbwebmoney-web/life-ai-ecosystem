from app.services.finance_service import EXPENSE_CATEGORIES, category_from_record, parse_amount


def test_parse_amount_int():
    assert parse_amount("1500000") == 1500000.0


def test_parse_amount_spaces():
    assert parse_amount("1 500 000") == 1500000.0


def test_parse_amount_comma():
    assert parse_amount("1500,50") == 1500.5


def test_parse_amount_invalid():
    assert parse_amount("abc") is None
    assert parse_amount("0") is None
    assert parse_amount("-100") is None


def test_category_from_record_empty():
    from app.models.entities import LifeRecord

    rec = LifeRecord(meta_json=None)
    assert category_from_record(rec) == "other"


def test_category_from_record_valid():
    import json

    from app.models.entities import LifeRecord

    rec = LifeRecord(meta_json=json.dumps({"category": "food"}))
    assert category_from_record(rec) == "food"


def test_expense_categories():
    assert "food" in EXPENSE_CATEGORIES
    assert "transport" in EXPENSE_CATEGORIES
