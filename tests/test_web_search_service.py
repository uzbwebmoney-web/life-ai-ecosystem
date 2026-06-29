import pytest

from app.services.web_search_service import (
    build_search_queries,
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


def test_should_use_web_search_travel_module_question():
    use, force = should_use_web_search("kak oformit vizu v Yaponiyu?", module_id="travel")
    assert use is True
    assert force is False


def test_build_search_queries_migration_uz():
    queries = build_search_queries(
        "migratsiya uchun telegram guruh",
        language="uz",
        country="O'zbekiston",
    )
    assert any("t.me" in q.lower() or "telegram" in q.lower() for q in queries)
    assert any("migratsiya" in q.lower() for q in queries)


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
    text = await fetch_web_context("migratsiya telegram", language="uz")
    assert "t.me/test_channel" in text
    assert "Telegram havolalar" in text
