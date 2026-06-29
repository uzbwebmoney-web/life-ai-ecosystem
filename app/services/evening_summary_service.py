from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.analytics_service import analyze_fitness_gaps, analyze_spending_period, format_spending_analysis
from app.services.dashboard_service import user_local_now, _collect_notifications, _format_relative
from app.services.ecosystem_service import list_unified_notifications
from app.services.organizer_service import list_tasks
from app.core.i18n import t


async def build_evening_summary(session: AsyncSession, user: User, *, lang: str | None = None) -> str:
    lang = lang or user.language
    now = user_local_now(user)
    lines = [f"🌙 <b>{t(lang, 'evening_summary_title')}</b>", ""]

    tasks = await list_tasks(session, user.id)
    done = [x for x in tasks if x.done]
    open_tasks = [x for x in tasks if not x.done]
    lines.append(t(lang, "evening_tasks_done", n=len(done)))
    if open_tasks:
        lines.append(t(lang, "evening_tasks_open", n=len(open_tasks)))
        for tk in open_tasks[:3]:
            lines.append(f"• {tk.title}")

    items = await list_unified_notifications(session, user, lang, horizon_days=7, limit=15)
    tomorrow = (now.date()).toordinal() + 1
    tomorrow_items = [i for i in items if i.sort_at.date().toordinal() == tomorrow]
    if tomorrow_items:
        lines.append(f"\n📅 <b>{t(lang, 'evening_tomorrow')}</b>")
        for item in tomorrow_items[:5]:
            lines.append(f"• {_format_relative(item.sort_at, now, lang)} — {item.title}")

    spending = await analyze_spending_period(session, user, days=7)
    if spending.record_count:
        lines.append(f"\n{format_spending_analysis(spending, lang=lang)[:350]}")

    fitness = await analyze_fitness_gaps(session, user, days=7)
    lines.append(f"\n{fitness}")

    alerts = [
        i
        for i in items
        if (i.sort_at.date().toordinal() - now.date().toordinal()) <= 7
        and any(k in i.title.lower() for k in ("страх", "insurance", "sug'urta"))
    ]
    for item in alerts[:2]:
        lines.append(t(lang, "evening_expiring", title=item.title, when=_format_relative(item.sort_at, now, lang)))

    lines.append(f"\n💡 {t(lang, 'evening_tip')}")
    return "\n".join(lines)
