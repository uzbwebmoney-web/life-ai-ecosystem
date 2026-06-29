from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.entities import User
from app.services.dashboard_service import build_daily_feed as compose_daily_feed
from app.services.dashboard_service import user_local_now
from app.services.evening_summary_service import build_evening_summary

logger = logging.getLogger(__name__)


class DailyFeedWorker:
    def __init__(self, poll_seconds: int = 120) -> None:
        self.poll_seconds = poll_seconds
        self._task: asyncio.Task | None = None

    def start(self, bot: Bot, session_maker: async_sessionmaker) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._loop(bot, session_maker))

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self, bot: Bot, session_maker: async_sessionmaker) -> None:
        while True:
            try:
                await self._tick(bot, session_maker)
            except Exception:
                logger.exception("Daily feed worker tick failed")
            await asyncio.sleep(self.poll_seconds)

    async def _tick(self, bot: Bot, session_maker: async_sessionmaker) -> None:
        async with session_maker() as session:
            users = (await session.execute(select(User).where(User.onboarding_done.is_(True)))).scalars().all()
        for user in users:
            now = user_local_now(user)
            day_key = now.strftime("%Y-%m-%d")
            try:
                if now.hour == 8 and user.last_daily_feed_date != day_key:
                    async with session_maker() as session:
                        text = await compose_daily_feed(session, user, user.language)
                    await bot.send_message(chat_id=int(user.telegram_id), text=text)
                    async with session_maker() as session:
                        db_user = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
                        db_user.last_daily_feed_date = day_key
                        await session.commit()
                if now.hour == 20 and getattr(user, "last_evening_feed_date", None) != day_key:
                    async with session_maker() as session:
                        text = await build_evening_summary(session, user)
                    await bot.send_message(chat_id=int(user.telegram_id), text=text)
                    async with session_maker() as session:
                        db_user = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
                        db_user.last_evening_feed_date = day_key
                        await session.commit()
            except Exception:
                logger.exception("Daily/evening feed failed user_id=%s", user.id)


daily_feed_worker = DailyFeedWorker()
