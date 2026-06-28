from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.car_service import (
    build_compliance_reminder_text,
    build_maint_reminder_text,
    fetch_car_compliance_due,
    fetch_car_maintenance_due,
    mark_car_compliance_notified,
    mark_car_maintenance_notified,
)
from app.services.finance_service import (
    build_bill_reminder_text,
    fetch_finance_bills_due,
    mark_finance_bill_notified,
)
from app.services.home_service import (
    build_utility_reminder_text,
    fetch_home_utilities_due,
    mark_home_utility_notified,
)
from app.services.health_service import build_med_reminder_text, fetch_med_reminders_due, mark_med_notified
from app.services.life_data import fetch_due_reminders, mark_reminder_sent

logger = logging.getLogger(__name__)


class ReminderWorker:
    def __init__(self, poll_seconds: int = 30) -> None:
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
                logger.exception("Reminder worker tick failed")
            await asyncio.sleep(self.poll_seconds)

    async def _tick(self, bot: Bot, session_maker: async_sessionmaker) -> None:
        async with session_maker() as session:
            due = await fetch_due_reminders(session)
            med_due = await fetch_med_reminders_due(session)
            car_maint_due = await fetch_car_maintenance_due(session)
            car_comp_due = await fetch_car_compliance_due(session)
            bill_due = await fetch_finance_bills_due(session)
            utility_due = await fetch_home_utilities_due(session)
        for reminder, user in due:
            try:
                prefix = "🩺" if reminder.module_id == "health" else "🔔"
                label = "Напоминание" if user.language == "ru" else "Reminder"
                if user.language == "uz":
                    label = "Eslatma"
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=f"{prefix} <b>{label}</b>\n\n{reminder.title}",
                )
                async with session_maker() as session:
                    await mark_reminder_sent(session, reminder.id)
            except Exception:
                logger.exception("Failed to send reminder id=%s", reminder.id)
        for med, user, notify_key in med_due:
            try:
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=build_med_reminder_text(med, user.language),
                )
                async with session_maker() as session:
                    await mark_med_notified(session, med.id, notify_key)
            except Exception:
                logger.exception("Failed to send med reminder med_id=%s", med.id)
        for item, user in car_maint_due:
            try:
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=build_maint_reminder_text(item, user.language),
                )
                async with session_maker() as session:
                    await mark_car_maintenance_notified(session, item.id)
            except Exception:
                logger.exception("Failed to send car maint reminder id=%s", item.id)
        for row, user, days_left in car_comp_due:
            try:
                key = f"{row.id}:{days_left}:{row.expires_at.date().isoformat()}"
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=build_compliance_reminder_text(row, days_left, user.language),
                )
                async with session_maker() as session:
                    await mark_car_compliance_notified(session, row.id, key)
            except Exception:
                logger.exception("Failed to send car compliance reminder id=%s", row.id)
        for bill, user in bill_due:
            try:
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=build_bill_reminder_text(bill, user.language),
                )
                async with session_maker() as session:
                    await mark_finance_bill_notified(session, bill.id)
            except Exception:
                logger.exception("Failed to send finance bill reminder id=%s", bill.id)
        for bill, user in utility_due:
            try:
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=build_utility_reminder_text(bill, user.language),
                )
                async with session_maker() as session:
                    await mark_home_utility_notified(session, bill.id)
            except Exception:
                logger.exception("Failed to send home utility reminder id=%s", bill.id)


reminder_worker = ReminderWorker()
