from app.core.plans import usd_to_stars
from app.services.payment_service import (
    build_stars_payload,
    parse_stars_payload,
    product_label,
    resolve_product,
    resolve_product_stars,
)


def test_resolve_product_plan():
    product_type, product_id, amount = resolve_product("premium")
    assert product_type == "plan"
    assert product_id == "premium"
    assert amount == 180_000


def test_resolve_product_package():
    product_type, product_id, amount = resolve_product("p_gpt54_500")
    assert product_type == "package"
    assert product_id == "p_gpt54_500"
    assert amount == 60_000


def test_resolve_product_free_raises():
    try:
        resolve_product("free")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_product_label_plan():
    label = product_label("plan", "basic", lang="ru")
    assert "Basic" in label


def test_product_label_package():
    label = product_label("package", "p_gpt54_500", lang="ru")
    assert "GPT-5.4" in label


def test_usd_to_stars():
    assert usd_to_stars(7.99) == 600
    assert usd_to_stars(14.99) == 1_100


def test_stars_payload_roundtrip():
    payload = build_stars_payload("plan", "premium")
    assert parse_stars_payload(payload) == ("plan", "premium")
    _, _, stars = resolve_product_stars("premium")
    assert stars == 1_100
