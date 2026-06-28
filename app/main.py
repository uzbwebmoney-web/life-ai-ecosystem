import asyncio

import logging



from aiohttp import web

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application



from app.bot.factory import create_bot, create_dispatcher

from app.core.config import settings

from app.database.session import SessionLocal, init_db

from app.services.reminder_worker import reminder_worker





async def main() -> None:

    logging.basicConfig(level=logging.INFO)

    await init_db()

    bot = create_bot()

    dp = create_dispatcher(SessionLocal)

    reminder_worker.start(bot, SessionLocal)

    logging.info("Life AI Ecosystem — 14 modules, voice, OCR, family, reminders")

    try:

        if settings.webhook_url.strip():

            app = web.Application()

            handler = SimpleRequestHandler(dispatcher=dp, bot=bot)

            handler.register(app, path=settings.webhook_path)

            setup_application(app, dp, bot=bot)

            await bot.set_webhook(f"{settings.webhook_url.rstrip('/')}{settings.webhook_path}")

            runner = web.AppRunner(app)

            await runner.setup()

            site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)

            await site.start()

            logging.info("Webhook mode: %s%s", settings.webhook_url, settings.webhook_path)

            await asyncio.Event().wait()

        else:

            await dp.start_polling(bot)

    finally:

        await reminder_worker.stop()





if __name__ == "__main__":

    asyncio.run(main())

