from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.life_data import get_or_create_user


class DbUserMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = data.get("event_from_user")
        if from_user and not getattr(from_user, "is_bot", False):
            async with self.session_maker() as session:
                user = await get_or_create_user(
                    session,
                    int(from_user.id),
                    from_user.username,
                    language_code=getattr(from_user, "language_code", None),
                )
                data["user"] = user
                data["session"] = session
                return await handler(event, data)
        return await handler(event, data)
