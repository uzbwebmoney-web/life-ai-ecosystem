from __future__ import annotations

from app.core.i18n import normalize_lang
from app.core.modules.catalog import MODULE_BY_ID

_MODULE_DISCLAIMERS: dict[str, dict[str, str]] = {
    "health": {
        "ru": "Не ставь диагноз и не назначай лечение — только справочная информация.",
        "uz": "Tashxis qo'ymang va davolash buyurmang — faqat ma'lumot.",
        "en": "Do not diagnose or prescribe — informational guidance only.",
    },
    "legal": {
        "ru": "Не замена юриста — общая информация и порядок действий.",
        "uz": "Yurist o'rnini bosmaydi — umumiy ma'lumot va tartib.",
        "en": "Not a lawyer — general information and next steps only.",
    },
    "emergency": {
        "ru": "При угрозе жизни звоните 103, 112.",
        "uz": "Hayot xavfi bo'lsa 103, 112 ga qo'ng'iroq qiling.",
        "en": "If life is at risk, call emergency services immediately.",
    },
    "finance": {
        "ru": "Не давай гарантий доходности.",
        "uz": "Daromad kafolati bermang.",
        "en": "Do not guarantee returns.",
    },
    "business": {
        "ru": "Не замена юриста, бухгалтера или маркетолога — черновики и общие рекомендации.",
        "uz": "Yurist, buxgalter yoki marketolog o'rnini bosmaydi — qoralama va umumiy maslahatlar.",
        "en": "Not a lawyer, accountant, or marketer — drafts and general guidance only.",
    },
    "car": {
        "ru": "Не замена диагностики СТО — только ориентиры.",
        "uz": "STO diagnostikasi o'rnini bosmaydi — faqat yo'naltirish.",
        "en": "Not a substitute for professional diagnostics.",
    },
    "travel": {
        "ru": "Визы и курсы — справочно; проверяйте на официальных источниках перед поездкой.",
        "uz": "Viza va kurslar — ma'lumot; sayohatdan oldin rasmiy manbalardan tekshiring.",
        "en": "Visa and rates are informational — verify with official sources before travel.",
    },
    "shopping": {
        "ru": "Цены и наличие — ориентиры; проверяйте в магазине перед покупкой.",
        "uz": "Narx va mavjudlik — yo'naltirish; sotib olishdan oldin do'konda tekshiring.",
        "en": "Prices and availability are estimates — verify in store before buying.",
    },
    "education": {
        "ru": "Помогай понять материал, не списывай за ученика — объясняй ошибки.",
        "uz": "Materialni tushunishga yordam bering, o'quvchi o'rniga yozmang — xatolarni tushuntiring.",
        "en": "Help understand the material — explain mistakes, do not do the work for the student.",
    },
    "nutrition": {
        "ru": "Не замена диетолога — общие рекомендации, учитывай индивидуальные особенности.",
        "uz": "Dietolog o'rnini bosmaydi — umumiy tavsiyalar, individual xususiyatlarni hisobga oling.",
        "en": "Not a dietitian — general guidance; consider individual health needs.",
    },
    "vault": {
        "ru": "Конфиденциальные данные — хранятся локально, не передавайте бот третьим лицам.",
        "uz": "Maxfiy ma'lumotlar — mahalliy saqlanadi, botni uchinchi shaxslarga bermang.",
        "en": "Confidential data — stored locally; do not share the bot with others.",
    },
}


def build_module_ai_hint(module_id: str, submodule_id: str | None = None, *, lang: str = "ru") -> str:
    mod = MODULE_BY_ID.get(module_id)
    if not mod:
        return ""

    code = normalize_lang(lang)
    module_title = mod.title(code)
    parts = [
        f"Ты — AI-помощник модуля «{module_title}» в экосистеме Life AI.",
        "Отвечай ТОЛЬКО в рамках этой темы. Не переключайся на другие модули без явной просьбы.",
        f"Специализация: {mod.ai_hint_ru}",
    ]

    if submodule_id:
        sub = next((s for s in mod.submodules if s.id == submodule_id), None)
        if sub:
            parts.append(f"Активный раздел: «{sub.title(code)}» — отвечай по этому подразделу.")
            if module_id == "health":
                from app.services.health_service import HEALTH_SUBMODULE_AI

                extra = HEALTH_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "car":
                from app.services.car_service import CAR_SUBMODULE_AI

                extra = CAR_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "finance":
                from app.services.finance_service import FINANCE_SUBMODULE_AI

                extra = FINANCE_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "business":
                from app.services.business_service import BUSINESS_SUBMODULE_AI

                extra = BUSINESS_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "legal":
                from app.services.legal_service import LEGAL_SUBMODULE_AI

                extra = LEGAL_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "travel":
                from app.services.travel_service import TRAVEL_SUBMODULE_AI

                extra = TRAVEL_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "home":
                from app.services.home_service import HOME_SUBMODULE_AI

                extra = HOME_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "shopping":
                from app.services.shopping_service import SHOPPING_SUBMODULE_AI

                extra = SHOPPING_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "education":
                from app.services.education_service import EDUCATION_SUBMODULE_AI

                extra = EDUCATION_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "nutrition":
                from app.services.nutrition_service import NUTRITION_SUBMODULE_AI

                extra = NUTRITION_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)
            if module_id == "ai_assistant":
                from app.services.assistant_service import ASSISTANT_SUBMODULE_AI

                extra = ASSISTANT_SUBMODULE_AI.get(submodule_id)
                if extra:
                    parts.append(extra)

    disclaimer = _MODULE_DISCLAIMERS.get(module_id, {}).get(code)
    if disclaimer:
        parts.append(f"Disclaimer: {disclaimer}")

    return " ".join(parts)


def active_module_label(module_id: str | None, submodule_id: str | None = None, *, lang: str = "ru") -> str:
    if not module_id:
        return ""
    mod = MODULE_BY_ID.get(module_id)
    if not mod:
        return ""
    code = normalize_lang(lang)
    if submodule_id:
        sub = next((s for s in mod.submodules if s.id == submodule_id), None)
        if sub:
            return f"{mod.emoji} {mod.title(code)} → {sub.title(code)}"
    return f"{mod.emoji} {mod.title(code)}"
