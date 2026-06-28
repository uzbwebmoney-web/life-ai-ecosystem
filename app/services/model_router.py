from __future__ import annotations

import re
from enum import Enum

from app.models.entities import User
from app.services.subscription_service import plan_info


class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"
    EXPERT = "expert"


_SIMPLE_RE = re.compile(
    r"^(?:"
    r"привет|здравств|спасибо|ок|okay|ok|yes|no|да|нет|hello|hi|thanks|"
    r"как дела|что умеешь|help|помощь|menu|меню"
    r")\b",
    re.IGNORECASE,
)

_EXPERT_KEYWORDS = (
    "стратег",
    "архитект",
    "юридич",
    "договор",
    "контракт",
    "риск",
    "due diligence",
    "compare",
    "comparison",
    "сравни",
    "проанализируй",
    "глубокий анализ",
    "business plan",
    "бизнес-план",
    "инвест",
    "налог",
    "compliance",
    "регулятор",
    "litigation",
    "иск",
    "arbitr",
)

_COMPLEX_KEYWORDS = (
    "анализ",
    "analyze",
    "analysis",
    "explain",
    "объясни",
    "почему",
    "why",
    "how to",
    "как ",
    "plan",
    "план",
    "calculate",
    "рассчит",
    "optimize",
    "оптимиз",
    "review",
    "провер",
    "diagnos",
    "диагн",
    "рекоменд",
    "recommend",
    "summarize",
    "конспект",
    "перевед",
    "translate",
    "код",
    "code",
    "sql",
    "python",
)

_EXPERT_MODULES = frozenset({"legal", "business", "finance"})


def classify_query_complexity(
    text: str,
    *,
    module_hint: str = "",
    module_id: str | None = None,
) -> QueryComplexity:
    raw = (text or "").strip()
    lower = raw.lower()
    words = raw.split()
    word_count = len(words)

    if not raw:
        return QueryComplexity.STANDARD

    if word_count <= 6 and (_SIMPLE_RE.match(lower) or (lower.endswith("?") and word_count <= 4)):
        if not any(k in lower for k in _COMPLEX_KEYWORDS + _EXPERT_KEYWORDS):
            return QueryComplexity.SIMPLE

    module = (module_id or module_hint or "").lower()

    if any(k in lower for k in _EXPERT_KEYWORDS):
        return QueryComplexity.EXPERT
    if word_count >= 120:
        return QueryComplexity.EXPERT
    if module in _EXPERT_MODULES and word_count >= 25:
        return QueryComplexity.EXPERT

    if any(k in lower for k in _COMPLEX_KEYWORDS):
        return QueryComplexity.COMPLEX
    if word_count >= 45:
        return QueryComplexity.COMPLEX
    if module in _EXPERT_MODULES and word_count >= 12:
        return QueryComplexity.COMPLEX

    if word_count <= 12 and "?" not in raw:
        return QueryComplexity.SIMPLE

    return QueryComplexity.STANDARD


def _base_model() -> str:
    from app.core.config import settings

    return settings.openai_model


def _advanced_model() -> str:
    from app.core.config import settings

    return settings.effective_advanced_model


def _pro_top_model() -> str:
    from app.core.config import settings

    return settings.effective_pro_model


def select_ai_model(
    user: User,
    user_message: str,
    *,
    module_hint: str = "",
    module_id: str | None = None,
) -> str:
    limits = plan_info(user).limits
    mode = limits.advanced_model
    base = _base_model()
    advanced = _advanced_model()
    top = _pro_top_model()

    complexity = classify_query_complexity(
        user_message,
        module_hint=module_hint,
        module_id=module_id,
    )

    if mode == "none":
        return base

    if mode == "limited":
        if complexity in (QueryComplexity.COMPLEX, QueryComplexity.EXPERT):
            return advanced
        return base

    if mode == "full":
        return advanced

    if mode == "router":
        if complexity == QueryComplexity.SIMPLE:
            return base
        if complexity == QueryComplexity.EXPERT:
            return top
        return advanced

    return base


def select_vision_model(
    user: User,
    *,
    module_id: str | None = None,
    caption: str = "",
    legal_document: bool = False,
    car_dashboard: bool = False,
) -> str:
    hint = caption.strip()
    if not hint:
        if legal_document:
            hint = "Юридический документ: детальный анализ условий и рисков"
        elif car_dashboard:
            hint = "Фото панели авто: диагностика ошибок и рекомендации"
        else:
            hint = "Анализ изображения: распознавание текста и содержимого"
    return select_ai_model(user, hint, module_id=module_id or "ai_assistant")


def model_routing_label(user: User, *, lang: str) -> str:
    from app.core.i18n import t

    limits = plan_info(user).limits
    mode = limits.advanced_model
    if mode == "none":
        return t(lang, "plan_model_none")
    if mode == "limited":
        return t(lang, "plan_model_limited", cap="—", model="GPT-5.4 Mini")
    if mode == "full":
        return t(lang, "plan_model_full", model="GPT-5.4 Mini")
    if mode == "router":
        return t(
            lang,
            "plan_model_router",
            top=_pro_top_model(),
            advanced=_advanced_model(),
            base=_base_model(),
        )
    return _base_model()
