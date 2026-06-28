from app.services.payment_service import product_label, resolve_product


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
