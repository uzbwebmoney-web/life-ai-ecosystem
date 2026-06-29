from app.services.text_format import format_ai_reply, format_ai_reply_html


def test_broken_markdown_link_converted_to_url():
    raw = "1. Sekis ([shapes.inc](https://shapes.inc/sekis/faq?utm_source=openai"
    cleaned = format_ai_reply(raw)
    assert "([shapes.inc]" not in cleaned
    assert "https://shapes.inc/sekis/faq" in cleaned


def test_full_markdown_link_converted():
    raw = "See [Example Site](https://example.com/page) for details."
    cleaned = format_ai_reply(raw)
    assert "[Example Site]" not in cleaned
    assert "https://example.com/page" in cleaned


def test_html_link_uses_domain_label():
    raw = "Visit https://shapes.inc/sekis/faq for info."
    html = format_ai_reply_html(raw)
    assert '<a href="https://shapes.inc/sekis/faq">shapes.inc</a>' in html
