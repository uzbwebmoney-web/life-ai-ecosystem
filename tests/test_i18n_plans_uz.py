from app.core.i18n import t
from app.core.i18n.extra_strings import EXTRA_RU, EXTRA_UZ
from app.services.subscription_service import format_plan_card


def test_uz_plan_strings_not_fallback_to_russian():
    plan_prefixes = (
        "plan_",
        "sub_plans",
        "sub_usage",
        "sub_current",
        "sub_trial",
        "sub_paid",
        "sub_ai_model",
        "sub_packages",
        "sub_addon",
        "sub_gpt",
    )
    missing = [
        k
        for k in sorted(EXTRA_RU)
        if any(k.startswith(p) or k == p for p in plan_prefixes) and k not in EXTRA_UZ
    ]
    assert missing == []


def test_format_plan_card_uz_uses_uzbek():
    text = format_plan_card("basic", lang="uz")
    assert "GPT-5.4 Mini" in text
    assert "ovoz" in text.lower() or "Ovoz" in text
    assert "Что включено" not in text
    assert t("uz", "plan_features_title") in text
