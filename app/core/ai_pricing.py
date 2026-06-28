from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ImageQuality = Literal["low", "medium", "high"]

# USD per 1M tokens (input, output) — chat models
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-5.4-mini": (0.75, 4.50),
    "gpt-5.5": (5.00, 30.00),
}

IMAGE_MODEL_KEY = "gpt-image-1"

# gpt-image-1 token rates (USD per 1M tokens)
IMAGE_TOKEN_PRICING: dict[str, float] = {
    "text_in": 5.00,
    "image_in": 10.00,
    "image_out": 40.00,
}

# gpt-image-1 flat rate per 1024×1024 image by quality tier
IMAGE_QUALITY_USD: dict[ImageQuality, float] = {
    "low": 0.011,
    "medium": 0.042,
    "high": 0.167,
}

PLAN_IMAGE_QUALITY: dict[str, ImageQuality] = {
    "basic": "low",
    "student": "low",
    "premium": "medium",
    "pro": "high",
}


@dataclass(frozen=True)
class ModelUsageRow:
    model_key: str
    requests: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    image_count: int = 0
    image_quality: str | None = None


@dataclass(frozen=True)
class ImageUsageSummary:
    count: int
    cost_usd: float
    by_quality: dict[str, tuple[int, float]]


def normalize_model_key(model: str) -> str:
    m = (model or "").lower()
    if "gpt-image" in m or m.startswith("dall-e"):
        return IMAGE_MODEL_KEY if "gpt-image" in m else m
    if "5.5" in m:
        return "gpt-5.5"
    if "5.4" in m or ("gpt-5" in m and "mini" in m):
        return "gpt-5.4-mini"
    if "4o-mini" in m or "gpt-4o" in m:
        return "gpt-4o-mini"
    from app.core.config import settings

    if m == settings.effective_pro_model.lower():
        return "gpt-5.5"
    if m == settings.effective_advanced_model.lower():
        return "gpt-5.4-mini"
    if m == settings.openai_model.lower():
        return "gpt-4o-mini"
    return "gpt-4o-mini"


def image_quality_for_plan(plan_id: str) -> ImageQuality:
    return PLAN_IMAGE_QUALITY.get(normalize_plan_id(plan_id), "medium")


def normalize_plan_id(plan_id: str) -> str:
    from app.core.plans import normalize_plan_id as _norm

    return _norm(plan_id)


def calc_image_cost_usd(quality: str | None, count: int = 1) -> float:
    if count <= 0:
        return 0.0
    q = (quality or "medium").lower()
    if q not in IMAGE_QUALITY_USD:
        q = "medium"
    return count * IMAGE_QUALITY_USD[q]  # type: ignore[index]


def calc_cost_usd(
    model_key: str,
    prompt_tokens: int,
    completion_tokens: int,
    *,
    image_count: int = 0,
    image_quality: str | None = None,
) -> float:
    if model_key == IMAGE_MODEL_KEY:
        if image_count > 0:
            return calc_image_cost_usd(image_quality, image_count)
        if prompt_tokens or completion_tokens:
            return (
                prompt_tokens * IMAGE_TOKEN_PRICING["text_in"]
                + completion_tokens * IMAGE_TOKEN_PRICING["image_out"]
            ) / 1_000_000
        return 0.0
    inp, out = MODEL_PRICING.get(model_key, MODEL_PRICING["gpt-4o-mini"])
    return (prompt_tokens * inp + completion_tokens * out) / 1_000_000


def format_usd(amount: float) -> str:
    if amount < 0.01:
        return f"${amount:.4f}"
    if amount < 1:
        return f"${amount:.3f}"
    return f"${amount:.2f}"


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def admin_rates_lines() -> list[str]:
    lines = [
        "<b>💬 Текст (input / output за 1M токенов):</b>",
        "• gpt-4o-mini — $0.15 / $0.60",
        "• gpt-5.4-mini — $0.75 / $4.50",
        "• gpt-5.5 — $5.00 / $30.00",
        "",
        f"<b>🎨 {IMAGE_MODEL_KEY} (1024×1024):</b>",
        f"• Low — {format_usd(IMAGE_QUALITY_USD['low'])}/шт • "
        f"Medium — {format_usd(IMAGE_QUALITY_USD['medium'])}/шт • "
        f"High — {format_usd(IMAGE_QUALITY_USD['high'])}/шт",
        f"• 500 шт: Low ≈ {format_usd(500 * IMAGE_QUALITY_USD['low'])} • "
        f"Medium ≈ {format_usd(500 * IMAGE_QUALITY_USD['medium'])} • "
        f"High ≈ {format_usd(500 * IMAGE_QUALITY_USD['high'])}",
        f"• Токены: text in ${IMAGE_TOKEN_PRICING['text_in']:.0f} • "
        f"image in ${IMAGE_TOKEN_PRICING['image_in']:.0f} • "
        f"image out ${IMAGE_TOKEN_PRICING['image_out']:.0f} / 1M",
    ]
    return lines
