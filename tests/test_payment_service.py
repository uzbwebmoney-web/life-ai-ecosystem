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
    assert amount == 144_000


def test_resolve_product_package():
    product_type, product_id, amount = resolve_product("p_credits_5000")
    assert product_type == "package"
    assert product_id == "p_credits_5000"
    assert amount == 72_000


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
    label = product_label("package", "p_credits_5000", lang="ru")
    assert "5000" in label


def test_usd_to_stars():
    assert usd_to_stars(5.99) == 450
    assert usd_to_stars(11.99) == 900


def test_stars_payload_roundtrip():
    payload = build_stars_payload("plan", "premium")
    assert parse_stars_payload(payload) == ("plan", "premium")
    _, _, stars = resolve_product_stars("premium")
    assert stars == 900
