from __future__ import annotations

import re

_AGENT_ACTION_RE = re.compile(
    r"|".join(
        (
            r"напомни|eslatma|remind me|set reminder",
            r"сохрани|saqlang|save (?:this|the|my)?",
            r"запиши|yozib qo'y|add (?:expense|record|task|note)",
            r"добавь|qo'sh|create project|yangi loyiha|новый проект",
            r"где (?:мой|моя|мои)|qayerda|where is|where's my",
            r"когда (?:я|мы)|qachon|when did",
            r"покажи чек|show receipt|chekni ko'rsat",
            r"найди (?:лучш|дешев|cheap|best)|compare|solishtir|сравни",
            r"сделай таблиц|make (?:a )?table|jadval",
            r"исследован|research report|chuqur tahlil|глубокий анализ",
            r"объясни (?:договор|контракт|document)|explain (?:contract|document)",
            r"анализ (?:расход|истори|трат)|spending analysis|xarajat tahlili",
            r"составь маршрут|plan trip|sayohat reja",
            r"проверь виз|visa check|viza",
            r"замени масло|change oil|yog' almashtir",
            r"гаранти|warranty|kafolat",
            r"инвентар|inventory|inventar",
            r"выполни|bajar|do this for me|сделай за меня",
        )
    ),
    re.IGNORECASE,
)

_RESEARCH_RE = re.compile(r"исследован|research|отч[её]т|report|chuqur tahlil", re.I)
_TEACHER_RE = re.compile(r"режим преподав|teacher mode|o'qituvchi rejimi|объясни тему и провер", re.I)
_TRAINER_RE = re.compile(r"режим тренер|trainer mode|murabbiy|ai-тренер|ai trener", re.I)


def should_route_to_agent(text: str, *, has_photo: bool = False, has_document: bool = False) -> bool:
    t = (text or "").strip()
    if has_photo or has_document:
        return True
    if len(t) < 4:
        return False
    return bool(_AGENT_ACTION_RE.search(t))


def detect_special_mode(text: str) -> str | None:
    t = (text or "").strip()
    if _TEACHER_RE.search(t):
        return "teacher"
    if _TRAINER_RE.search(t):
        return "trainer"
    if _RESEARCH_RE.search(t):
        return "research"
    return None
