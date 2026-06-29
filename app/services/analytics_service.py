from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import LifeRecord, OrganizerItem, User
from app.services.dashboard_service import user_local_now
from app.services.finance_service import category_from_record, current_month_key
from app.services.household_service import effective_data_user_ids


@dataclass
class SpendingAnalysis:
    period_days: int
    total: float
    by_category: dict[str, float] = field(default_factory=dict)
    prev_total: float = 0.0
    change_pct: float = 0.0
    top_category: str = ""
    record_count: int = 0


async def analyze_spending_period(session: AsyncSession, user: User, *, days: int = 30) -> SpendingAnalysis:
    user_ids = await effective_data_user_ids(session, user)
    now = user_local_now(user)
    start = now - timedelta(days=days)
    prev_start = start - timedelta(days=days)
    rows = (
        await session.execute(
            select(LifeRecord).where(
                LifeRecord.user_id.in_(user_ids),
                LifeRecord.module_id == "finance",
                LifeRecord.submodule_id == "expense",
                LifeRecord.created_at >= prev_start,
            )
        )
    ).scalars().all()
    current_total = 0.0
    prev_total = 0.0
    by_cat: dict[str, float] = {}
    count = 0
    for rec in rows:
        amt = float(rec.amount or 0)
        if rec.created_at >= start:
            current_total += amt
            cat = category_from_record(rec)
            by_cat[cat] = by_cat.get(cat, 0.0) + amt
            count += 1
        elif rec.created_at >= prev_start:
            prev_total += amt
    change = 0.0
    if prev_total > 0:
        change = ((current_total - prev_total) / prev_total) * 100
    top = max(by_cat, key=by_cat.get) if by_cat else ""
    return SpendingAnalysis(
        period_days=days,
        total=current_total,
        by_category=by_cat,
        prev_total=prev_total,
        change_pct=change,
        top_category=top,
        record_count=count,
    )


def format_spending_analysis(data: SpendingAnalysis, *, lang: str = "ru") -> str:
    from app.core.i18n import t

    lines = [
        t(lang, "agent_spending_title", days=data.period_days),
        t(lang, "agent_spending_total", total=f"{data.total:,.0f}"),
    ]
    if data.change_pct:
        direction = t(lang, "agent_spending_up") if data.change_pct > 0 else t(lang, "agent_spending_down")
        lines.append(t(lang, "agent_spending_change", pct=abs(round(data.change_pct, 1)), direction=direction))
    if data.by_category:
        lines.append(t(lang, "agent_spending_by_cat"))
        for cat, amt in sorted(data.by_category.items(), key=lambda x: -x[1])[:6]:
            lines.append(f"• {cat}: {amt:,.0f} UZS")
    return "\n".join(lines)


async def analyze_fitness_gaps(session: AsyncSession, user: User, *, days: int = 30) -> str:
    from app.core.i18n import t

    lang = user.language
    start = user_local_now(user) - timedelta(days=days)
    tasks = (
        await session.execute(
            select(OrganizerItem).where(
                OrganizerItem.user_id == user.id,
                OrganizerItem.item_type == "task",
                or_(
                    OrganizerItem.title.ilike("%тренир%"),
                    OrganizerItem.title.ilike("%workout%"),
                    OrganizerItem.title.ilike("%mashq%"),
                ),
                OrganizerItem.created_at >= start,
            )
        )
    ).scalars().all()
    done = sum(1 for t in tasks if t.done)
    missed = sum(1 for t in tasks if not t.done and t.due_at and t.due_at < user_local_now(user))
    if not tasks and not missed:
        return t(lang, "agent_fitness_no_data")
    return t(lang, "agent_fitness_stats", done=done, missed=missed, total=len(tasks))


def build_expense_chart_png(analysis: SpendingAnalysis) -> bytes | None:
    if not analysis.by_category:
        return None
    try:
        import io

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = list(analysis.by_category.keys())
        values = list(analysis.by_category.values())
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, values)
        ax.set_title("Expenses by category")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return buf.getvalue()
    except Exception:
        return None
