from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.analytics_service import analyze_fitness_gaps, analyze_spending_period, format_spending_analysis
from app.services.car_service import list_car_compliance, list_car_maintenance
from app.services.credit_loans import list_credit_loans_for_users, loan_remaining
from app.services.dashboard_service import build_dashboard, user_local_now
from app.services.finance_service import finance_total
from app.services.household_service import effective_data_user_ids
from app.services.organizer_service import list_tasks
from app.services.health_service import list_health_medications
from app.services.subscription_service import plan_info
from app.services.travel_service import UNIT_PER_USD, convert_currency, format_currency_amount
from app.services.weather_service import fetch_weather_summary
from app.core.i18n import t


async def build_today_dashboard(session: AsyncSession, user: User, *, lang: str | None = None) -> str:
    lang = lang or user.language
    base = await build_dashboard(session, user, lang)
    lines = [f"📊 <b>{t(lang, 'today_full_title')}</b>", "", base.text, ""]

    now = user_local_now(user)
    user_ids = await effective_data_user_ids(session, user)

    income = 0.0
    expense = 0.0
    for uid in user_ids:
        income += await finance_total(session, uid, "income")
        expense += await finance_total(session, uid, "expense")
    lines.append(f"💰 <b>{t(lang, 'today_finance')}</b>")
    lines.append(t(lang, "today_finance_line", income=f"{income:,.0f}", expense=f"{expense:,.0f}"))

    spending = await analyze_spending_period(session, user, days=30)
    if spending.record_count:
        lines.append(format_spending_analysis(spending, lang=lang)[:400])

    loans = await list_credit_loans_for_users(session, user_ids)
    if loans:
        lines.append(f"\n💳 <b>{t(lang, 'today_credits')}</b>")
        for loan in loans[:3]:
            rem = loan_remaining(loan)
            lines.append(f"• {loan.title}: {rem:,.0f} UZS (день {loan.payment_day})")

    maint = await list_car_maintenance(session, user.id)
    compliance = await list_car_compliance(session, user.id)
    if maint or compliance:
        lines.append(f"\n🚗 <b>{t(lang, 'today_car')}</b>")
        for item in maint[:2]:
            lines.append(f"• {item.title}")
        for item in compliance[:2]:
            lines.append(f"• {item.title}")

    tasks = await list_tasks(session, user.id)
    done_today = [tk for tk in tasks if tk.done]
    open_tasks = [tk for tk in tasks if not tk.done][:5]
    lines.append(f"\n✅ <b>{t(lang, 'today_tasks')}</b>")
    lines.append(t(lang, "today_tasks_done", n=len(done_today)))
    for tk in open_tasks:
        lines.append(f"• {tk.title}")

    meds = await list_health_medications(session, user.id)
    if meds:
        lines.append(f"\n💊 <b>{t(lang, 'today_meds')}</b>")
        for med in meds[:4]:
            lines.append(f"• {med.name}")

    fitness = await analyze_fitness_gaps(session, user, days=14)
    lines.append(f"\n🏋️ {fitness}")

    weather = await fetch_weather_summary(lang=lang, utc_offset_minutes=user.utc_offset_minutes or 300)
    if weather:
        lines.append(f"\n{weather}")

    usd_uzs = format_currency_amount(UNIT_PER_USD["UZS"], "UZS")
    eur_val = convert_currency(1, "EUR", "UZS")
    eur_uzs = format_currency_amount(eur_val or 0, "UZS")
    lines.append(f"\n💱 <b>{t(lang, 'today_fx')}</b>")
    lines.append(t(lang, "today_fx_line", usd=usd_uzs, eur=eur_uzs))

    pinfo = plan_info(user)
    lines.append(f"\n⭐ <b>{t(lang, 'today_subscription')}</b>")
    lines.append(t(lang, "today_subscription_line", plan=t(lang, pinfo.name_key), emoji=pinfo.emoji))

    lines.append(f"\n📰 {t(lang, 'today_news_hint')}")
    lines.append(f"\n💡 {t(lang, 'dash_daily_tip')}")
    return "\n".join(lines)
