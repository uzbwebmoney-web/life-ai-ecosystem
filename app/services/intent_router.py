from __future__ import annotations

import re
from urllib.parse import urlparse

from app.services.module_context import build_module_ai_hint

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "health": ("здоров", "симптом", "лекарств", "давлен", "анализ", "врач", "болит"),
    "car": ("машин", "авто", "масл", "то ", "техосмотр", "штраф", "бензин", "двигател"),
    "finance": ("деньг", "расход", "доход", "бюджет", "кредит", "долг", "подписк", "инвест"),
    "business": ("бизнес", "маркетинг", "конкурент", "реклам", "продаж", "клиент", "стартап", "crm"),
    "legal": ("закон", "договор", "жалоб", "наслед", "юрист", "суд", "заявлен", "иск", "право", "документ"),
    "travel": ("виза", "билет", "отель", "путешеств", "рейс", "маршрут", "чемодан", "валют", "перевод"),
    "home": ("дом", "коммунал", "квартир", "ремонт", "инвентар", "холодильник", "свет", "газ", "вода"),
    "shopping": ("купить", "товар", "скидк", "маркетплейс", "ozon", "aliexpress", "сравн", "характеристик"),
    "education": ("учеб", "экзамен", "дз", "домашн", "конспект", "урок", "формул", "язык", "граммат"),
    "organizer": ("задач", "календар", "напомин", "встреч", "день рожд", "заметк", "органайзер"),
    "ai_assistant": ("перевод", "translate", "tarjima", "нарис", "картин", "dall", "программ", "python", "код", "debug"),
    "vault": ("хранилищ", "омbor", "vault", "паспорт", "полис", "гарант", "чек", "архив"),
    "nutrition": ("калори", "диет", "рецепт", "еда", "рацион", "белок", "вода", "питани"),
    "emergency": ("экстрен", "дтп", "скорую", "103", "112", "первая помощь"),
    "security": ("мошен", "ссылк", "фишинг", "безопас", "вирус"),
    "ecology": ("погод", "воздух", "uv", "пыльц"),
}


def detect_module(text: str) -> str | None:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for module_id, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lowered)
        if score:
            scores[module_id] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def module_hint(module_id: str, submodule_id: str | None = None, *, lang: str = "ru") -> str:
    return build_module_ai_hint(module_id, submodule_id, lang=lang)


def check_url_security(url: str) -> dict[str, str]:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return {"risk": "high", "summary": "Некорректная или небезопасная схема URL."}
    host = (parsed.netloc or "").lower()
    flags: list[str] = []
    if re.search(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        flags.append("IP-адрес вместо домена")
    if host.count("-") >= 3:
        flags.append("Подозрительно много дефисов в домене")
    if any(tld in host for tld in (".xyz", ".top", ".click", ".loan")):
        flags.append("Редкий/рискованный домен")
    if "login" in parsed.path.lower() or "verify" in parsed.path.lower():
        flags.append("Путь похож на фишинг (login/verify)")
    if not flags:
        return {"risk": "low", "summary": "Явных признаков фишинга не найдено. Всё равно будьте осторожны."}
    risk = "high" if len(flags) >= 2 else "medium"
    return {"risk": risk, "summary": "; ".join(flags)}
