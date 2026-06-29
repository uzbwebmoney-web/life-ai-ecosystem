from __future__ import annotations

from app.core.i18n import normalize_lang

ECOSYSTEM_NAME: dict[str, str] = {
    "ru": "Моя жизнь",
    "uz": "Mening hayotim",
    "en": "My Life",
}


def ecosystem_name(lang: str) -> str:
    return ECOSYSTEM_NAME.get(normalize_lang(lang), ECOSYSTEM_NAME["ru"])


def ai_assistant_system_identity(lang: str) -> str:
    code = normalize_lang(lang)
    brand = ecosystem_name(code)
    if code == "uz":
        return (
            f"Sen — «{brand}» AI ekotizimining shaxsiy yordamchisisan. "
            "O'zingni faqat shu nom bilan tanishtir, «Life AI» deb atama. "
        )
    if code == "en":
        return (
            f"You are the personal AI assistant of the «{brand}» ecosystem. "
            "Introduce yourself only with this name, never as «Life AI». "
        )
    return (
        f"Ты — личный AI-помощник экосистемы «{brand}». "
        "Представляйся только так, не называй себя «Life AI» или «помощник Life AI». "
    )


def module_ai_system_identity(module_title: str, lang: str) -> str:
    code = normalize_lang(lang)
    brand = ecosystem_name(code)
    if code == "uz":
        return f"Sen — «{module_title}» moduli AI yordamchisisan, «{brand}» ekotizimida."
    if code == "en":
        return (
            f"You are the AI assistant for the «{module_title}» module "
            f"in the «{brand}» ecosystem."
        )
    return f"Ты — AI-помощник модуля «{module_title}» в экосистеме «{brand}»."
