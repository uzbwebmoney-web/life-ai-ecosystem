from __future__ import annotations

import re

_PAGE_PATTERNS = (
    re.compile(r"(\d+)\s*(?:стр(?:ани(?:ц|ы|a))?|pages?|sahifa|bet)", re.I),
    re.compile(r"(?:на|for)\s*(\d+)\s*(?:стр|page|sahifa)", re.I),
)

_DETAIL_KEYWORDS = (
    "подробн",
    "разверн",
    "развёрн",
    "полный",
    "полностью",
    "детальн",
    "объёмн",
    "обемн",
    "глубок",
    "расширен",
    "много",
    "detailed",
    "comprehensive",
    "in depth",
    "full notes",
    "batafsil",
    "to'liq",
    "keng",
)

_BRIEF_KEYWORDS = (
    "кратко",
    "коротко",
    "1 страниц",
    "одной страниц",
    "one page",
    "short",
    "qisqa",
)


def parse_requested_pages(text: str) -> int | None:
    low = (text or "").lower()
    for pattern in _PAGE_PATTERNS:
        match = pattern.search(low)
        if match:
            pages = int(match.group(1))
            if 1 <= pages <= 30:
                return pages
    return None


def wants_detailed_notes(text: str) -> bool:
    low = (text or "").lower()
    return any(k in low for k in _DETAIL_KEYWORDS)


def wants_brief_notes(text: str) -> bool:
    low = (text or "").lower()
    return any(k in low for k in _BRIEF_KEYWORDS)


def completion_limit_for_notes(user_message: str) -> int:
    if wants_brief_notes(user_message):
        return 1800
    pages = parse_requested_pages(user_message)
    if pages:
        return min(max(pages * 900, 2500), 12_000)
    if wants_detailed_notes(user_message):
        return 6500
    return 4500


def study_notes_depth_instruction(user_message: str) -> str:
    if wants_brief_notes(user_message):
        return "Сделай краткий конспект на 1 страницу: только главное, структурированно."
    pages = parse_requested_pages(user_message)
    if pages:
        return (
            f"Сделай развёрнутый учебный конспект объёмом примерно на {pages} страниц A4 "
            f"(ориентир ~2500–3000 знаков на страницу). "
            "Не ограничивайся тезисами: для каждого раздела дай определения, пояснения, "
            "примеры, связи с практикой. Структура: введение, основные разделы с подпунктами, "
            "сравнения где уместно, вывод. Пиши связным грамотным языком."
        )
    if wants_detailed_notes(user_message):
        return (
            "Сделай подробный полноценный конспект: не сокращай до 5–10 пунктов. "
            "Раскрой тему глубоко, с примерами и выводами."
        )
    return (
        "Сделай содержательный структурированный конспект среднего объёма (2–4 страницы): "
        "определения, пояснения, примеры, вывод — не только список тезисов."
    )


def prepare_study_notes_request(
    module_id: str,
    submodule_id: str | None,
    user_message: str,
    hint: str,
) -> tuple[str, str, int]:
    if module_id != "education" or submodule_id != "notes":
        return user_message, hint, 1200
    enriched_hint = f"{hint}\n\n{study_notes_depth_instruction(user_message)}"
    return user_message, enriched_hint, completion_limit_for_notes(user_message)
