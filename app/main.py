import asyncio
import logging

from app.bot.factory import create_bot, create_dispatcher
from app.database.session import SessionLocal, init_db
from app.services.reminder_worker import reminder_worker


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()
    bot = create_bot()
    dp = create_dispatcher(SessionLocal)
    reminder_worker.start(bot, SessionLocal)
    logging.info("Life AI Ecosystem — 30 modules, voice, OCR, family, reminders")
    try:
        await dp.start_polling(bot)
    finally:
        await reminder_worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
