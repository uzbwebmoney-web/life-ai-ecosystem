from unittest.mock import Mock

from app.core.ai_pricing import admin_rates_lines
from app.services.ai_usage_service import AiCostStats, extract_usage, format_ai_cost_stats_message


def test_extract_usage_chat_tokens():
    response = Mock(usage=Mock(prompt_tokens=100, completion_tokens=50))
    assert extract_usage(response) == (100, 50)


def test_extract_usage_image_tokens():
    response = Mock(usage=Mock(input_tokens=12, output_tokens=420, spec=["input_tokens", "output_tokens"]))
    assert extract_usage(response) == (12, 420)


def test_extract_usage_missing_usage():
    assert extract_usage(Mock(usage=None)) == (0, 0)


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
