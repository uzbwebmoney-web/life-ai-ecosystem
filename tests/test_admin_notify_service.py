from unittest.mock import AsyncMock, MagicMock, patch

from app.models.entities import User
from app.services.admin_notify_service import _format_utc_offset, notify_admins_ai_request, notify_admins_new_user


def test_format_utc_offset():
    assert _format_utc_offset(300) == "UTC+05:00"
    assert _format_utc_offset(-120) == "UTC-02:00"


def test_notify_admins_new_user_skips_when_disabled():
    bot = AsyncMock()
    user = User(id=1, telegram_id=123, username="tester", language="uz", plan_id="free")

    async def _run():
        with patch("app.services.admin_notify_service.settings") as settings:
            settings.admin_new_user_notify = False
            settings.admin_telegram_id_list = [999]
            await notify_admins_new_user(bot, user, telegram_lang="uz")

    import asyncio

    asyncio.run(_run())
    bot.send_message.assert_not_called()


def test_notify_admins_new_user_sends_to_admins():
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    user = User(id=1, telegram_id=8159351732, username="buriev2", language="uz", plan_id="free")

    async def _run():
        with patch("app.services.admin_notify_service.settings") as settings:
            settings.admin_new_user_notify = True
            settings.admin_telegram_id_list = [940679235]
            await notify_admins_new_user(bot, user, telegram_lang="uz")

    import asyncio

    asyncio.run(_run())
    bot.send_message.assert_awaited_once()
    text = bot.send_message.await_args.kwargs.get("text") or bot.send_message.await_args.args[1]
    assert "8159351732" in text
    assert "buriev2" in text


def test_notify_admins_ai_request_includes_preview():
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    user = User(id=2, telegram_id=8382460911, username="feruzbek_5559", language="uz")

    async def _run():
        with patch("app.services.admin_notify_service.settings") as settings:
            settings.admin_ai_request_notify = True
            settings.admin_telegram_id_list = [940679235]
            await notify_admins_ai_request(
                bot,
                user,
                model="gpt-4o-mini",
                source="chat",
                prompt_tokens=100,
                completion_tokens=50,
                preview="Как спланировать бюджет?",
            )

    import asyncio

    asyncio.run(_run())
    text = bot.send_message.await_args.kwargs.get("text") or bot.send_message.await_args.args[1]
    assert "8382460911" in text
    assert "gpt-4o-mini" in text
    assert "бюджет" in text
