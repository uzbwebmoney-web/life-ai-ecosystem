from app.services.intent_router import check_url_security, detect_module


def test_detect_health_intent():
    assert detect_module("у меня болит голова и температура") == "health"


def test_detect_finance_intent():
    assert detect_module("сколько я потратил на расходы в этом месяце") == "finance"


def test_url_security_flags_ip():
    result = check_url_security("http://192.168.1.1/login")
    assert result["risk"] in {"medium", "high"}


def test_url_security_clean_domain():
    result = check_url_security("https://example.com/about")
    assert result["risk"] == "low"
