from app.core.i18n import LANG_LABELS, normalize_lang, t
from app.services.intent_router import module_hint


def test_normalize_lang():
    assert normalize_lang("uz-UZ") == "uz"
    assert normalize_lang("en") == "en"
    assert normalize_lang("de") == "ru"


def test_three_languages_welcome():
    assert "Моя жизнь" in t("ru", "welcome")
    assert "Mening hayotim" in t("uz", "welcome")
    assert "My Life" in t("en", "welcome")


def test_language_labels():
    assert len(LANG_LABELS) == 3


def test_module_hint_uzbek():
    hint = module_hint("legal", "applications", lang="uz")
    assert "Yuridik" in hint or "yuridik" in hint.lower() or "huquq" in hint.lower()
