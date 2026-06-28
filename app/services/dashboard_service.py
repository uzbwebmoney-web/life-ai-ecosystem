from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import User
from app.services.credit_loans import list_credit_loans, list_credit_loans_for_users, loan_remaining
from app.services.ecosystem_service import EcosystemNotification, list_unified_notifications
from app.services.household_service import effective_data_user_ids
from app.services.weather_service import fetch_weather_summary


@dataclass
class DashboardData:
    text: str


def user_local_now(user: User) -> datetime:
    return datetime.utcnow() + timedelta(minutes=user.utc_offset_minutes or 0)


def _greeting_key(hour: int) -> str:
    if 5 <= hour < 12:
        return "dash_greeting_morning"
    if 12 <= hour < 18:
        return "dash_greeting_day"
    if 18 <= hour < 23:
        return "dash_greeting_evening"
    return "dash_greeting_night"


def _format_relative(when: datetime, now: datetime, lang: str) -> str:
    delta = when - now
    minutes = int(delta.total_seconds() // 60)
    if minutes < 0:
        return t(lang, "dash_time_now")
    if minutes < 60:
        return t(lang, "dash_time_in_min", n=minutes)
    hours = minutes // 60
    if hours < 24:
        return t(lang, "dash_time_in_hours", n=hours)
    days = hours // 24
    if days == 1:
        return t(lang, "dash_time_tomorrow")
    return t(lang, "dash_time_in_days", n=days)


async def _collect_notifications(session: AsyncSession, user: User, lang: str) -> list[EcosystemNotification]:
    return await list_unified_notifications(session, user, lang, horizon_days=14, limit=25)


async def build_dashboard(session: AsyncSession, user: User, lang: str, *, display_name: str | None = None) -> DashboardData:
    now = user_local_now(user)
    name = (display_name or user.username or t(lang, "dash_friend")).strip()
    greeting = t(lang, _greeting_key(now.hour), name=name)
    lines = [greeting, ""]

    items = await _collect_notifications(session, user, lang)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    today_lines: list[str] = []
    timeline_lines: list[str] = []

    for item in items:
        rel = _format_relative(item.sort_at, now, lang)
        line = f"{item.icon} {rel} — {item.title}"
        item_date = item.sort_at.date()
        if item_date == today or (item_date == tomorrow and item.sort_at.hour < 12):
            today_lines.append(line)
        elif today <= item_date <= today + timedelta(days=7):
            timeline_lines.append(f"• {item.sort_at.strftime('%d.%m')} {item.icon} {item.title}")

    user_ids = await effective_data_user_ids(session, user)
    for loan in await list_credit_loans_for_users(session, user_ids):
        remaining = loan_remaining(loan)
        suffix = f" ({t(lang, 'credits_remaining_short', remaining=int(remaining))})" if remaining > 0 else ""
        if loan.payment_day == now.day:
            today_lines.append(f"💳 {t(lang, 'dash_credit_today', title=loan.title)}{suffix}")
        elif loan.payment_day == (now + timedelta(days=1)).day:
            today_lines.append(f"💳 {t(lang, 'dash_credit_tomorrow', title=loan.title)}{suffix}")

    lines.append(f"📅 <b>{t(lang, 'dash_today')}</b>")
    if today_lines:
        lines.extend(today_lines[:8])
    else:
        lines.append(t(lang, "dash_today_empty"))

    if timeline_lines:
        lines.extend(["", f"🗓 <b>{t(lang, 'dash_timeline')}</b>", *timeline_lines[:6]])

    weather = await fetch_weather_summary(lang=lang, utc_offset_minutes=user.utc_offset_minutes or 300)
    if weather:
        lines.extend(["", f"🌦 {weather.split(chr(10))[0]}"])

    lines.extend(["", f"<b>{t(lang, 'dash_what_todo')}</b>"])
    return DashboardData(text="\n".join(lines))


async def build_daily_feed(session: AsyncSession, user: User, lang: str, *, display_name: str | None = None) -> str:
    dash = await build_dashboard(session, user, lang, display_name=display_name)
    tip = t(lang, "dash_daily_tip")
    return f"{t(lang, 'dash_morning_title')}\n\n{dash.text}\n\n💡 {tip}"
