from __future__ import annotations

import re

_PAGE_PATTERNS = (
    re.compile(r"(\d+)\s*(?:стр(?:ани(?:ц|ы|a))?|pages?|sahifa|bet)", re.I),
    re.compile(r"(?:на|for)\s*(\d+)\s*(?:стр|page|sahifa|bet)", re.I),
)

_DETAIL_KEYWORDS = (
    "подробн",
    "разверн",
    "развёрн",
    "полный",
    "полностью",
    "детальн",
    "объёмн",
    "объемн",
    "обемн",
    "глубок",
    "расширен",
    "много",
    "больш",
    "объем",
    "объём",
    "раскрыт",
    "развернут",
    "detailed",
    "comprehensive",
    "in depth",
    "full notes",
    "voluminous",
    "lengthy",
    "long form",
    "batafsil",
    "to'liq",
    "to‘liq",
    "keng",
    "katta",
    "ko'p",
    "ko‘p",
    "kop",
    "hajmli",
    "juda ko'p",
    "juda kop",
    "chuqur",
    "keng qamrov",
)

_MEGA_DETAIL_KEYWORDS = (
    "juda katta",
    "juda ko'p",
    "juda kop",
    "очень больш",
    "максималь",
    "maksimal",
    "maximum",
    "20 bet",
    "25 bet",
    "30 bet",
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

_STUDY_DOC_KEYWORDS = (
    "конспект",
    "konspekt",
    "реферат",
    "referat",
    "referát",
    "maqola",
    "essay",
    "coursework",
    "курсов",
    "o'quv ishi",
    "o‘quv ishi",
    "lecture note",
    "study notes",
)

_CHAT_FORMAT_HINTS = (
    "в чат",
    "в чате",
    "текстом",
    "просто текст",
    "oddiy matn",
    "matn ko'rinish",
    "matn ko‘rinish",
    "text only",
    "in chat",
    "chatda",
)

_DEFAULT_MEDIUM_PAGES = 4
_DEFAULT_DETAILED_PAGES = 10
_DEFAULT_MEGA_PAGES = 15


def parse_requested_pages(text: str) -> int | None:
    low = (text or "").lower()
    for pattern in _PAGE_PATTERNS:
        match = pattern.search(low)
        if match:
            pages = int(match.group(1))
            if 1 <= pages <= 50:
                return pages
    return None


def wants_detailed_notes(text: str) -> bool:
    low = (text or "").lower()
    return any(k in low for k in _DETAIL_KEYWORDS)


def wants_mega_notes(text: str) -> bool:
    low = (text or "").lower()
    pages = parse_requested_pages(text)
    if pages is not None and pages >= 15:
        return True
    return any(k in low for k in _MEGA_DETAIL_KEYWORDS)


def format_specified(text: str) -> bool:
    from app.services.study_document_service import detect_export_format

    if detect_export_format(text):
        return True
    low = (text or "").lower()
    return any(h in low for h in _CHAT_FORMAT_HINTS)


def pages_specified(text: str) -> bool:
    return (
        parse_requested_pages(text) is not None
        or wants_brief_notes(text)
        or wants_detailed_notes(text)
    )


def effective_page_count(text: str) -> int:
    pages = parse_requested_pages(text)
    if pages:
        return pages
    if wants_brief_notes(text):
        return 1
    if wants_mega_notes(text):
        return _DEFAULT_MEGA_PAGES
    if wants_detailed_notes(text):
        return _DEFAULT_DETAILED_PAGES
    return _DEFAULT_MEDIUM_PAGES


def is_study_document_request(module_id: str, submodule_id: str | None, user_message: str) -> bool:
    if module_id != "education":
        return False
    if submodule_id in {"notes", "exams"}:
        return True
    low = (user_message or "").lower()
    return any(k in low for k in _STUDY_DOC_KEYWORDS)


def needs_study_document_clarification(
    module_id: str,
    submodule_id: str | None,
    user_message: str,
) -> bool:
    if not is_study_document_request(module_id, submodule_id, user_message):
        return False
    return not pages_specified(user_message)


def combine_study_request(topic: str, spec: str) -> str:
    topic = (topic or "").strip()
    spec = (spec or "").strip()
    if not spec:
        return topic
    if not topic:
        return spec
    return f"{topic}\n\n{spec}"


def study_spec_from_callback(pages: int, fmt: str) -> str:
    if fmt == "chat":
        return (
            f"Развёрнутый конспект/реферат в чате, примерно {pages} страниц A4. "
            "Раскрой тему полностью: введение, разделы с подпунктами, примеры, вывод."
        )
    if fmt == "pdf":
        return (
            f"Развёрнутый конспект/реферат на {pages} страниц A4, оформи и выдай в PDF. "
            "Раскрой тему полностью."
        )
    if fmt == "docx":
        return (
            f"Развёрнутый конспект/реферат на {pages} страниц A4, оформи и выдай в Word (DOCX). "
            "Раскрой тему полностью."
        )
    return f"Развёрнутый конспект/реферат на {pages} страниц A4."


def wants_brief_notes(text: str) -> bool:
    low = (text or "").lower()
    return any(k in low for k in _BRIEF_KEYWORDS)


def completion_limit_for_notes(user_message: str) -> int:
    if wants_brief_notes(user_message):
        return 1800
    pages = effective_page_count(user_message)
    return min(max(pages * 900, 2500), 45000)


def study_notes_depth_instruction(user_message: str) -> str:
    if wants_brief_notes(user_message):
        return "Сделай краткий конспект на 1 страницу: только главное, структурированно."
    pages = effective_page_count(user_message)
    return (
        f"Сделай развёрнутый учебный конспект/реферат объёмом примерно на {pages} страниц A4 "
        f"(ориентир ~2500–3000 знаков на страницу). "
        "Не ограничивайся тезисами: для каждого раздела дай определения, пояснения, "
        "примеры, связи с практикой. Структура: введение, основные разделы с подпунктами, "
        "сравнения где уместно, вывод. Пиши связным грамотным языком. "
        "Не сокращай ответ — пользователь просил объёмный материал."
    )


def _is_notes_request(module_id: str, submodule_id: str | None, user_message: str) -> bool:
    return is_study_document_request(module_id, submodule_id, user_message)


def prepare_study_notes_request(
    module_id: str,
    submodule_id: str | None,
    user_message: str,
    hint: str,
) -> tuple[str, str, int]:
    if not _is_notes_request(module_id, submodule_id, user_message):
        return user_message, hint, 1200
    enriched_hint = f"{hint}\n\n{study_notes_depth_instruction(user_message)}"
    return user_message, enriched_hint, completion_limit_for_notes(user_message)
