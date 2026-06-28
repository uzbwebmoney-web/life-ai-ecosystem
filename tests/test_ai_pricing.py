from app.core.ai_pricing import calc_cost_usd, format_usd, normalize_model_key


def test_normalize_model_key():
    assert normalize_model_key("gpt-4o-mini") == "gpt-4o-mini"
    assert normalize_model_key("gpt-5.4-mini") == "gpt-5.4-mini"
    assert normalize_model_key("gpt-5.5") == "gpt-5.5"


def test_calc_cost_gpt4o_mini():
    # 1000 in + 500 out
    cost = calc_cost_usd("gpt-4o-mini", 1000, 500)
    assert abs(cost - (1000 * 0.15 + 500 * 0.60) / 1_000_000) < 1e-9


def test_calc_cost_gpt55():
    cost = calc_cost_usd("gpt-5.5", 10_000, 2000)
    expected = (10_000 * 5.0 + 2000 * 30.0) / 1_000_000
    assert abs(cost - expected) < 1e-9


def test_format_usd_small():
    assert format_usd(0.0012) == "$0.0012"
