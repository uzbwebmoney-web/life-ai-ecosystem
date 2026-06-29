import pytest

from app.services.text_format import format_ai_reply_html
from app.services.web_search_service import (
    append_links_footer,
    build_search_queries,
    collect_links_from_text,
    fetch_ddg_context,
    fetch_web_context,
    should_use_web_search,
)


def test_should_use_web_search_telegram_channel_ru():
    use, force = should_use_web_search("дай группу или телеграм канал агенства миграции")
    assert use is True
    assert force is True


def test_should_use_web_search_telegram_channel_uz():
    use, force = should_use_web_search("migratsiya agentligi telegram guruh havolasini bering")
    assert use is True
    assert force is True


def test_should_use_web_search_general_question():
    use, force = should_use_web_search("что такое фотосинтез")
    assert use is False
    assert force is False


def test_collect_links_from_handles_and_bare_tme():
    links = collect_links_from_text("Kanal @migration_uz yoki t.me/official_uz")
    assert "https://t.me/migration_uz" in links
    assert "https://t.me/official_uz" in links


def test_append_links_footer_adds_missing_links():
    answer = "Migratsiya kanali mavjud."
    links = ["https://t.me/migration_uz", "https://example.com"]
    out = append_links_footer(answer, links, language="uz")
    assert "https://t.me/migration_uz" in out
    assert "🔗 Havolalar" in out


def test_format_ai_reply_html_makes_links_clickable():
    html = format_ai_reply_html("Qarang: https://t.me/test")
    assert '<a href="https://t.me/test">https://t.me/test</a>' in html


def test_build_search_queries_migration_uz():
    queries = build_search_queries(
        "migratsiya uchun telegram guruh",
        language="uz",
        country="O'zbekiston",
    )
    assert any("telegram" in q.lower() for q in queries)


@pytest.mark.asyncio
async def test_fetch_ddg_context_returns_text(monkeypatch):
    class FakeResp:
        text = (
            '<a class="result-link" href="https://t.me/migration_uz">Migration UZ</a>'
            '<td class="result-snippet">Official telegram</td>'
        )

        def raise_for_status(self):
            return None

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, *args, **kwargs):
            return FakeResp()

    monkeypatch.setattr("app.services.web_search_service.httpx.AsyncClient", lambda **kwargs: FakeClient())
    text = await fetch_ddg_context("migration agency telegram")
    assert "Migration UZ" in text
    assert "t.me/migration_uz" in text


@pytest.mark.asyncio
async def test_fetch_web_context_extracts_tme_links(monkeypatch):
    class FakeResp:
        text = (
            '<a class="result-link" href="https://t.me/test_channel">Test</a>'
            '<td class="result-snippet">https://t.me/test_channel info</td>'
        )

        def raise_for_status(self):
            return None

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, *args, **kwargs):
            return FakeResp()

    monkeypatch.setattr("app.services.web_search_service.httpx.AsyncClient", lambda **kwargs: FakeClient())
    context, links = await fetch_web_context("migratsiya telegram", language="uz")
    assert "t.me/test_channel" in context
    assert any("t.me/test_channel" in link for link in links)
