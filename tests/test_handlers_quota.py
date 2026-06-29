import pytest

from app.bot.quota_ui import answer_quota_block, answer_quota_key
from app.services.subscription_service import format_insufficient_credits, parse_insufficient_credits_reply
from app.models.entities import User


class _Msg:
    def __init__(self):
        self.answers: list[tuple] = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


@pytest.mark.asyncio
async def test_answer_quota_block_strips_prefix():
    user = User(id=1, telegram_id=1, plan_id="free", ai_used_month=300)
    text = format_insufficient_credits(user, cost=3, lang="ru")
    msg = _Msg()
    await answer_quota_block(msg, text, lang="ru")
    assert len(msg.answers) == 1
    body, kwargs = msg.answers[0]
    assert "Недостаточно" in body
    assert kwargs.get("reply_markup") is not None
    assert parse_insufficient_credits_reply(text)[0]


@pytest.mark.asyncio
async def test_answer_quota_key():
    msg = _Msg()
    await answer_quota_key(msg, "quota_export", lang="ru")
    assert len(msg.answers) == 1
    assert "Student" in msg.answers[0][0] or "eksport" in msg.answers[0][0].lower() or "Экспорт" in msg.answers[0][0]
