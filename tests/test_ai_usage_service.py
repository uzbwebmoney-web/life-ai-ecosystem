from app.core.ai_pricing import admin_rates_lines
from app.services.ai_usage_service import AiCostStats, format_ai_cost_stats_message


def test_format_ai_cost_stats_includes_image_rates():
    stats = AiCostStats(month_images=50, month_image_cost=2.1)
    text = format_ai_cost_stats_message(stats, lang="ru")
    assert "gpt-image-1" in text
    assert "gpt-4o-mini" in text
    assert "50" in text
    assert "$0.011" in text or "0.011" in text


def test_admin_rates_lines():
    lines = admin_rates_lines()
    joined = "\n".join(lines)
    assert "gpt-image-1" in joined
    assert "500" in joined
