from app.core.ai_pricing import (
    IMAGE_MODEL_KEY,
    IMAGE_QUALITY_USD,
    calc_cost_usd,
    calc_image_cost_usd,
    format_usd,
    image_quality_for_plan,
    normalize_model_key,
)


def test_normalize_model_key():
    assert normalize_model_key("gpt-4o-mini") == "gpt-4o-mini"
    assert normalize_model_key("gpt-5.4-mini") == "gpt-5.4-mini"
    assert normalize_model_key("gpt-5.5") == "gpt-5.5"
    assert normalize_model_key("gpt-image-1") == IMAGE_MODEL_KEY


def test_calc_cost_gpt4o_mini():
    cost = calc_cost_usd("gpt-4o-mini", 1000, 500)
    assert abs(cost - (1000 * 0.15 + 500 * 0.60) / 1_000_000) < 1e-9


def test_calc_cost_gpt55():
    cost = calc_cost_usd("gpt-5.5", 10_000, 2000)
    expected = (10_000 * 5.0 + 2000 * 30.0) / 1_000_000
    assert abs(cost - expected) < 1e-9


def test_calc_image_cost_by_quality():
    assert calc_image_cost_usd("low", 1) == IMAGE_QUALITY_USD["low"]
    assert abs(calc_image_cost_usd("medium", 500) - 500 * 0.042) < 1e-9
    assert abs(calc_image_cost_usd("high", 500) - 500 * 0.167) < 1e-9


def test_calc_cost_gpt_image_with_count():
    cost = calc_cost_usd(IMAGE_MODEL_KEY, 0, 0, image_count=10, image_quality="medium")
    assert abs(cost - 10 * 0.042) < 1e-9


def test_image_quality_for_plan():
    assert image_quality_for_plan("basic") == "low"
    assert image_quality_for_plan("premium") == "medium"
    assert image_quality_for_plan("pro") == "high"
    assert image_quality_for_plan("student") == "low"


def test_format_usd_small():
    assert format_usd(0.0012) == "$0.0012"


def test_admin_rates_lines_include_image_model():
    text = "\n".join(__import__("app.core.ai_pricing", fromlist=["admin_rates_lines"]).admin_rates_lines())
    assert "gpt-image-1" in text
    assert "500" in text
