from __future__ import annotations

from dataclasses import dataclass

# USD per 1M tokens (input, output)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-5.4-mini": (0.75, 4.50),
    "gpt-5.5": (5.00, 30.00),
}


@dataclass(frozen=True)
class ModelUsageRow:
    model_key: str
    requests: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float


def normalize_model_key(model: str) -> str:
    m = (model or "").lower()
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


def calc_cost_usd(model_key: str, prompt_tokens: int, completion_tokens: int) -> float:
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
