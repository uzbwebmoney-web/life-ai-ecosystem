from app.bot.message_ui import TELEGRAM_SAFE_LIMIT, split_telegram_text


def test_split_short_text():
    text = "hello"
    assert split_telegram_text(text) == ["hello"]


def test_split_long_text():
    text = "a" * 9000
    chunks = split_telegram_text(text, limit=4000)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 4000 for chunk in chunks)
    assert "".join(chunks) == text


def test_split_preserves_lines():
    lines = [f"line {i}: {'x' * 100}" for i in range(50)]
    text = "\n".join(lines)
    chunks = split_telegram_text(text, limit=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
    for line in lines[:5]:
        assert any(line in chunk for chunk in chunks)
