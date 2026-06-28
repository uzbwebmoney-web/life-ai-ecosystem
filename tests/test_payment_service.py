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
    assert amount == 108_000


def test_resolve_product_package():
    product_type, product_id, amount = resolve_product("p100")
    assert product_type == "package"
    assert product_id == "p100"
    assert amount == 24_000


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
    label = product_label("package", "p500", lang="ru")
    assert "500" in label


def test_usd_to_stars():
    assert usd_to_stars(4) == 300
    assert usd_to_stars(9) == 700


def test_stars_payload_roundtrip():
    payload = build_stars_payload("plan", "premium")
    assert parse_stars_payload(payload) == ("plan", "premium")
    _, _, stars = resolve_product_stars("premium")
    assert stars == 700
