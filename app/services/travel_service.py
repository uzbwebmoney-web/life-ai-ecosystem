from __future__ import annotations

from app.core.i18n import t

# Units of currency per 1 USD (reference rates, no live API).
UNIT_PER_USD: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "RUB": 92.0,
    "UZS": 12_600.0,
    "KZT": 450.0,
    "TRY": 32.0,
    "CNY": 7.2,
    "AED": 3.67,
    "THB": 35.0,
}

TRAVEL_CURRENCIES: tuple[str, ...] = tuple(UNIT_PER_USD.keys())

TRAVEL_SUBMODULE_AI: dict[str, str] = {
    "routes": (
        "Помогай планировать маршруты: города, дни, достопримечательности, транспорт между точками, "
        "примерное время. Учитывай сезон и бюджет, если указаны."
    ),
    "visas": (
        "Давай справочную информацию о визах: нужна ли виза, типы, типичные документы, сроки, "
        "куда обращаться. Предупреждай, что правила меняются — проверять на сайте консульства."
    ),
    "budget": (
        "Помогай составить бюджет поездки: перелёт, жильё, еда, транспорт, развлечения, резерв. "
        "Разбивай по категориям и давай диапазоны."
    ),
    "packing": (
        "Составляй чек-листы вещей в поездку: одежда, документы, гигиена, техника, аптечка. "
        "Учитывай климат, длительность и тип поездки."
    ),
    "translator": (
        "Переводи фразы для путешествий, объясняй произношение, давай полезные фразы для аэропорта, "
        "отеля, ресторана, экстренных ситуаций."
    ),
    "currency": (
        "Объясняй валюты стран, даёшь ориентиры по курсам и советы по обмену. "
        "Для точного расчёта предложи встроенный конвертер."
    ),
}


def travel_submodule_description(sub_id: str, lang: str) -> str:
    key = f"trv_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else t(lang, "trv_ai_hint")


def parse_amount(raw: str) -> float | None:
    try:
        val = float(raw.replace(" ", "").replace(",", ".").strip())
        return val if val > 0 else None
    except ValueError:
        return None


def convert_currency(amount: float, from_code: str, to_code: str) -> float | None:
    from_code = from_code.upper()
    to_code = to_code.upper()
    if from_code not in UNIT_PER_USD or to_code not in UNIT_PER_USD:
        return None
    usd_amount = amount / UNIT_PER_USD[from_code]
    return usd_amount * UNIT_PER_USD[to_code]


def format_currency_amount(value: float, code: str) -> str:
    if code in ("UZS", "KZT", "RUB"):
        rounded = int(round(value))
        return f"{rounded:,}".replace(",", " ") + f" {code}"
    return f"{value:,.2f}".replace(",", " ") + f" {code}"
