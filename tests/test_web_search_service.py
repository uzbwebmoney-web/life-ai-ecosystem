import pytest

from app.services.web_search_service import (
    fetch_ddg_context,
    should_use_web_search,
)


def test_should_use_web_search_telegram_channel():
    use, force = should_use_web_search("дай группу или телеграм канал агенства миграции")
    assert use is True
    assert force is True


def test_should_use_web_search_general_question():
    use, force = should_use_web_search("что такое фотосинтез")
    assert use is False
    assert force is False


def test_should_use_web_search_travel_module_question():
    use, force = should_use_web_search("как оформить визу в Японию?", module_id="travel")
    assert use is True
    assert force is False


@pytest.mark.asyncio
async def test_fetch_ddg_context_returns_text(monkeypatch):
    class FakeResp:
        text = (
            '<a class="result-link" href="https://example.com">Example</a>'
            '<td class="result-snippet">Official site</td>'
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
    assert "Example" in text
    assert "example.com" in text
