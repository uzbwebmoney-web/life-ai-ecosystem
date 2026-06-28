from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.handlers.vault import router as vault_router
from app.bot.handlers.generic_ai import router as generic_ai_router
from app.bot.handlers.notifications import router as notifications_router
from app.bot.handlers.assistant import router as assistant_router, text_router as assistant_text_router
from app.bot.handlers.organizer import router as organizer_router
from app.bot.handlers.nutrition import router as nutrition_router
from app.bot.handlers.education import router as education_router
from app.bot.handlers.shopping import router as shopping_router
from app.bot.handlers.home import router as home_router
from app.bot.handlers.travel import router as travel_router
from app.bot.handlers.legal import router as legal_router
from app.bot.handlers.business import router as business_router
from app.bot.handlers.car import router as car_router
from app.bot.handlers.finance import router as finance_router
from app.bot.handlers.health import router as health_router
from app.bot.handlers.credits import router as credits_router
from app.bot.handlers.actions import router as actions_router
from app.bot.handlers.family import router as family_router
from app.bot.handlers.free_text import router as free_text_router
from app.bot.handlers.hub import router as hub_router
from app.bot.handlers.media import router as media_router
from app.bot.handlers.start import router as start_router
from app.bot.middlewares.db_user import DbUserMiddleware
from app.core.config import settings


def create_dispatcher(session_maker: async_sessionmaker) -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(DbUserMiddleware(session_maker))
    dp.callback_query.middleware(DbUserMiddleware(session_maker))
    dp.include_router(start_router)
    dp.include_router(health_router)
    dp.include_router(car_router)
    dp.include_router(finance_router)
    dp.include_router(business_router)
    dp.include_router(legal_router)
    dp.include_router(travel_router)
    dp.include_router(home_router)
    dp.include_router(shopping_router)
    dp.include_router(education_router)
    dp.include_router(nutrition_router)
    dp.include_router(organizer_router)
    dp.include_router(assistant_router)
    dp.include_router(vault_router)
    dp.include_router(generic_ai_router)
    dp.include_router(notifications_router)
    dp.include_router(credits_router)
    dp.include_router(hub_router)
    dp.include_router(family_router)
    dp.include_router(actions_router)
    dp.include_router(assistant_text_router)
    dp.include_router(media_router)
    dp.include_router(free_text_router)  # last: free-text intent router
    return dp


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
