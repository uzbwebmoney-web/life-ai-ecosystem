from __future__ import annotations

from app.models.entities import User


def personalization_system_note(user: User) -> str:
    parts: list[str] = []
    style = (user.response_style or "balanced").lower()
    level = (user.knowledge_level or "standard").lower()
    mode = (user.ui_mode or "normal").lower()

    style_map = {
        "brief": "Отвечай кратко, по делу, без воды.",
        "detailed": "Отвечай подробно с примерами и структурой.",
        "balanced": "Отвечай сбалансированно: краткое резюме + детали по запросу.",
        "friendly": "Дружелюбный тёплый тон, но профессионально.",
    }
    level_map = {
        "beginner": "Уровень пользователя: начинающий — объясняй простыми словами.",
        "standard": "Уровень пользователя: средний.",
        "expert": "Уровень пользователя: эксперт — можно использовать термины.",
    }
    if style in style_map:
        parts.append(style_map[style])
    if level in level_map:
        parts.append(level_map[level])
    if mode == "child":
        parts.append("Режим ребёнка: очень простые слова, короткие предложения, без сложных тем.")
    elif mode == "elder":
        parts.append("Режим пожилого человека: максимально простые формулировки, пошагово, спокойный тон.")
    return " ".join(parts)


def agent_reply_prefix(user: User, lang: str) -> str:
    from app.core.i18n import t

    if (user.ui_mode or "normal") == "child":
        return t(lang, "agent_prefix_child")
    if user.ui_mode == "elder":
        return t(lang, "agent_prefix_elder")
    return t(lang, "agent_prefix_default")
