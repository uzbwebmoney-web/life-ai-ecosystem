from app.core.branding import ai_assistant_system_identity, ecosystem_name, module_ai_system_identity


def test_ecosystem_name():
    assert ecosystem_name("ru") == "Моя жизнь"
    assert ecosystem_name("uz") == "Mening hayotim"
    assert ecosystem_name("en") == "My Life"


def test_ai_assistant_system_identity_uses_brand():
    assert ai_assistant_system_identity("ru").startswith(
        "Ты — личный AI-помощник экосистемы «Моя жизнь»"
    )
    assert "Mening hayotim" in ai_assistant_system_identity("uz")
    assert "My Life" in ai_assistant_system_identity("en")


def test_module_ai_system_identity():
    line = module_ai_system_identity("Здоровье", "ru")
    assert "Моя жизнь" in line
    assert "Здоровье" in line
