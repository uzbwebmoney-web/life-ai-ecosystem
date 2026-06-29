from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from app.core.ai_pricing import ImageQuality, normalize_model_key

# Internal coefficients — adjust when OpenAI prices or models change (users never see these).
INTERNAL_MODEL_FACTOR: dict[str, float] = {
    "gpt-4o-mini": 1.0,
    "gpt-5.4-mini": 1.1,
    "gpt-5.5": 1.25,
}

# User-facing action costs (AI credits).
ACTION_CREDITS = {
    "simple": 1,
    "translation": 1,
    "writing": 2,
    "health": 2,
    "finance": 2,
    "car": 2,
    "legal": 3,
    "business": 3,
    "pdf": 4,
    "photo": 4,
    "code": 5,
    "notes": 6,
    "notes_detailed": 10,
    "notes_10p": 15,
    "notes_20p": 30,
    "notes_50p": 70,
}

IMAGE_CREDITS: dict[ImageQuality, int] = {
    "low": 15,
    "medium": 30,
    "high": 60,
}

MODULE_BASE_ACTION: dict[str, str] = {
    "health": "health",
    "finance": "finance",
    "car": "car",
    "legal": "legal",
    "business": "business",
    "nutrition": "health",
    "fitness": "health",
}

TaskKind = Literal[
    "chat",
    "study_notes",
    "image_gen",
    "photo_analysis",
    "pdf_analysis",
    "code",
    "translation",
    "writing",
]


class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"
    EXPERT = "expert"


@dataclass(frozen=True)
class CreditEstimate:
    credits: int
    max_output_tokens: int
    model: str
    task_kind: TaskKind
    parts: int = 1
    chunk_tokens: int = 0


def _volume_factor(max_output_tokens: int) -> float:
    tokens = max(1, int(max_output_tokens))
    if tokens <= 4500:
        return 1.0
    if tokens <= 9000:
        return 1.05
    if tokens <= 18000:
        return 1.1
    return 1.15


def apply_internal_coefficients(base: int, *, model: str, max_output_tokens: int) -> int:
    """Map table cost → actual debit using hidden model/volume factors."""
    key = normalize_model_key(model)
    model_factor = INTERNAL_MODEL_FACTOR.get(key, 1.0)
    volume_factor = _volume_factor(max_output_tokens)
    return max(1, math.ceil(base * model_factor * volume_factor))


def image_generation_credits(quality: ImageQuality) -> int:
    return IMAGE_CREDITS.get(quality, IMAGE_CREDITS["medium"])


def photo_analysis_credits(*, multi: bool = False) -> int:
    base = ACTION_CREDITS["photo"]
    return base * 2 if multi else base


def _parse_pages(text: str) -> int | None:
    from app.services.study_notes_service import parse_requested_pages

    return parse_requested_pages(text)


def _wants_brief(text: str) -> bool:
    from app.services.study_notes_service import wants_brief_notes

    return wants_brief_notes(text)


def _wants_detailed(text: str) -> bool:
    from app.services.study_notes_service import wants_detailed_notes

    return wants_detailed_notes(text)


def study_notes_base_credits(user_message: str) -> int:
    pages = _parse_pages(user_message)
    if pages == 50:
        return ACTION_CREDITS["notes_50p"]
    if pages == 20:
        return ACTION_CREDITS["notes_20p"]
    if pages == 10:
        return ACTION_CREDITS["notes_10p"]
    if pages and pages > 10:
        return ACTION_CREDITS["notes_50p"] if pages >= 40 else ACTION_CREDITS["notes_20p"]
    if _wants_detailed(user_message):
        return ACTION_CREDITS["notes_detailed"]
    if _wants_brief(user_message):
        return ACTION_CREDITS["simple"]
    return ACTION_CREDITS["notes"]


def study_notes_output_tokens(user_message: str) -> int:
    from app.services.study_notes_service import completion_limit_for_notes

    return completion_limit_for_notes(user_message)


def detect_task_kind(
    *,
    user_message: str,
    module_id: str | None = None,
    submodule_id: str | None = None,
    source: str = "chat",
) -> TaskKind:
    low = (user_message or "").lower()
    mod = (module_id or "").lower()
    sub = (submodule_id or "").lower()

    if source == "image_gen":
        return "image_gen"
    if source in ("photo", "vision"):
        return "photo_analysis"
    if source == "pdf":
        return "pdf_analysis"

    if mod == "education" and (
        sub == "notes"
        or any(k in low for k in ("конспект", "konspekt", "реферат", "referat", "study notes", "maqola"))
    ):
        return "study_notes"
    if sub == "translate" or (mod == "ai_assistant" and sub == "translate"):
        return "translation"
    if sub == "writing" or (mod == "ai_assistant" and sub == "writing"):
        return "writing"
    if sub == "code" or (mod == "ai_assistant" and sub == "code"):
        return "code"
    if sub == "documents" and ("pdf" in low or ".pdf" in low):
        return "pdf_analysis"
    return "chat"


def _module_base_credits(module_id: str | None, submodule_id: str | None, complexity: QueryComplexity) -> int:
    mod = (module_id or "").lower()
    sub = (submodule_id or "").lower()
    if mod == "business" or sub in ("plans", "ads", "competitors", "contracts", "client_responses", "sales_analysis"):
        return ACTION_CREDITS["business"]
    if mod == "legal" or sub in ("questions", "doc_check", "applications", "legislation", "checklists"):
        return ACTION_CREDITS["legal"]
    action_key = MODULE_BASE_ACTION.get(mod)
    if action_key:
        return ACTION_CREDITS[action_key]
    if complexity == QueryComplexity.SIMPLE:
        return ACTION_CREDITS["simple"]
    return ACTION_CREDITS["writing"]


def estimate_request_credits(
    *,
    user_message: str,
    model: str,
    max_output_tokens: int,
    module_id: str | None = None,
    submodule_id: str | None = None,
    source: str = "chat",
    image_quality: ImageQuality | None = None,
    photo_multi: bool = False,
    pdf_pages: int | None = None,
    complexity: QueryComplexity = QueryComplexity.STANDARD,
) -> CreditEstimate:
    task_kind = detect_task_kind(
        user_message=user_message,
        module_id=module_id,
        submodule_id=submodule_id,
        source=source,
    )

    if task_kind == "image_gen":
        quality = image_quality or "medium"
        return CreditEstimate(image_generation_credits(quality), 0, model, task_kind)

    if task_kind == "photo_analysis":
        base = photo_analysis_credits(multi=photo_multi)
        credits = apply_internal_coefficients(base, model=model, max_output_tokens=1200)
        return CreditEstimate(credits, 1200, model, task_kind)

    if task_kind == "pdf_analysis":
        base = ACTION_CREDITS["pdf"]
        if pdf_pages and pdf_pages > 30:
            base = ACTION_CREDITS["pdf"] + 2
        tokens = min((pdf_pages or 10) * 600, 12000)
        credits = apply_internal_coefficients(base, model=model, max_output_tokens=tokens)
        return CreditEstimate(credits, tokens, model, task_kind)

    if task_kind == "study_notes":
        base = study_notes_base_credits(user_message)
        tokens = study_notes_output_tokens(user_message)
    elif task_kind == "translation":
        base = ACTION_CREDITS["translation"]
        tokens = min(max_output_tokens, 2000)
    elif task_kind == "writing":
        base = ACTION_CREDITS["writing"]
        tokens = max(max_output_tokens, 2500)
    elif task_kind == "code":
        base = ACTION_CREDITS["code"]
        tokens = max(max_output_tokens, 3000)
    else:
        base = _module_base_credits(module_id, submodule_id, complexity)
        tokens = max(max_output_tokens, 1200)

    credits = apply_internal_coefficients(base, model=model, max_output_tokens=tokens)
    return CreditEstimate(credits, tokens, model, task_kind)


def _guess_pdf_pages(text: str) -> int:
    match = re.search(r"(\d+)\s*(?:стр|page|bet|sahifa)", (text or "").lower())
    if match:
        return max(1, int(match.group(1)))
    return 10


def chunk_plan(max_output_tokens: int, chunk_size: int) -> tuple[int, int]:
    chunk_size = max(1500, chunk_size)
    parts = max(1, math.ceil(max_output_tokens / chunk_size))
    per_chunk = min(chunk_size, max_output_tokens)
    return parts, per_chunk


def apply_chunk_estimate(estimate: CreditEstimate, *, chunk_size: int) -> CreditEstimate:
    parts, per_chunk = chunk_plan(estimate.max_output_tokens, chunk_size)
    return CreditEstimate(
        credits=estimate.credits,
        max_output_tokens=estimate.max_output_tokens,
        model=estimate.model,
        task_kind=estimate.task_kind,
        parts=parts,
        chunk_tokens=per_chunk,
    )


def study_notes_credits(user_message: str) -> int:
    return study_notes_base_credits(user_message)


def credits_from_output_tokens(max_output_tokens: int) -> int:
    return apply_internal_coefficients(ACTION_CREDITS["writing"], model="gpt-4o-mini", max_output_tokens=max_output_tokens)
