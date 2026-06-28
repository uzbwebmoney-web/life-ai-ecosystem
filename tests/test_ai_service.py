from app.services.text_format import format_ai_reply


def test_strips_bold_markers():
    src = "1. **Какие симптомы** у вас есть?\n2. **Срочно обращайтесь**"
    out = format_ai_reply(src)
    assert "**" not in out
    assert "Какие симптомы" in out
    assert "Срочно обращайтесь" in out


def test_removes_orphan_asterisks():
    assert format_ai_reply("текст ** без пары") == "текст  без пары"
