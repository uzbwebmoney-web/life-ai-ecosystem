from __future__ import annotations

_NEW_TOKEN_PARAM_PREFIXES = ("o1", "o2", "o3", "o4", "gpt-5", "gpt-4.1", "gpt-4.5", "chatgpt-")


def chat_token_limit_kwargs(model: str, limit: int) -> dict[str, int]:
    model_l = model.lower()
    if any(p in model_l for p in _NEW_TOKEN_PARAM_PREFIXES):
        return {"max_completion_tokens": limit}
    return {"max_tokens": limit}
