from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_pricing import (
    ModelUsageRow,
    calc_cost_usd,
    format_tokens,
    format_usd,
    normalize_model_key,
)
from app.models.entities import AiUsageLog, User


def _utcnow() -> datetime:
    return datetime.utcnow()


def _day_start(days_ago: int = 0) -> datetime:
    now = datetime.utcnow()
    return (now - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)


def extract_usage(response) -> tuple[int, int]:
    usage = getattr(response, "usage", None)
    if not usage:
        return 0, 0
    return int(usage.prompt_tokens or 0), int(usage.completion_tokens or 0)


async def record_ai_usage(
    session: AsyncSession,
    user_id: int | None,
    model: str,
    response,
    *,
    source: str = "chat",
) -> None:
    prompt_tokens, completion_tokens = extract_usage(response)
    if prompt_tokens == 0 and completion_tokens == 0:
        return
    model_key = normalize_model_key(model)
    session.add(
        AiUsageLog(
            user_id=user_id,
            model=model,
            model_key=model_key,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            source=source,
        )
    )
    await session.commit()


@dataclass
class AiCostStats:
    today_cost: float = 0.0
    today_requests: int = 0
    week_cost: float = 0.0
    week_requests: int = 0
    month_cost: float = 0.0
    month_requests: int = 0
    total_cost: float = 0.0
    total_requests: int = 0
    month_by_model: list[ModelUsageRow] = field(default_factory=list)
    top_users_month: list[tuple[str, float, int]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


async def _aggregate_since(session: AsyncSession, since: datetime | None) -> tuple[float, int]:
    q = select(
        func.coalesce(func.sum(AiUsageLog.prompt_tokens), 0),
        func.coalesce(func.sum(AiUsageLog.completion_tokens), 0),
        func.count(AiUsageLog.id),
    )
    if since is not None:
        q = q.where(AiUsageLog.created_at >= since)
    prompt, completion, count = (await session.execute(q)).one()
    cost = 0.0
    if since is None:
        rows = (
            await session.execute(
                select(
                    AiUsageLog.model_key,
                    func.sum(AiUsageLog.prompt_tokens),
                    func.sum(AiUsageLog.completion_tokens),
                ).group_by(AiUsageLog.model_key)
            )
        ).all()
        for model_key, p, c in rows:
            cost += calc_cost_usd(model_key, int(p or 0), int(c or 0))
    else:
        rows = (
            await session.execute(
                select(
                    AiUsageLog.model_key,
                    func.sum(AiUsageLog.prompt_tokens),
                    func.sum(AiUsageLog.completion_tokens),
                )
                .where(AiUsageLog.created_at >= since)
                .group_by(AiUsageLog.model_key)
            )
        ).all()
        for model_key, p, c in rows:
            cost += calc_cost_usd(model_key, int(p or 0), int(c or 0))
    return cost, int(count or 0)


async def _by_model_since(session: AsyncSession, since: datetime) -> list[ModelUsageRow]:
    rows = (
        await session.execute(
            select(
                AiUsageLog.model_key,
                func.count(AiUsageLog.id),
                func.sum(AiUsageLog.prompt_tokens),
                func.sum(AiUsageLog.completion_tokens),
            )
            .where(AiUsageLog.created_at >= since)
            .group_by(AiUsageLog.model_key)
            .order_by(func.sum(AiUsageLog.prompt_tokens).desc())
        )
    ).all()
    result: list[ModelUsageRow] = []
    for model_key, requests, prompt, completion in rows:
        p = int(prompt or 0)
        c = int(completion or 0)
        result.append(
            ModelUsageRow(
                model_key=model_key,
                requests=int(requests or 0),
                prompt_tokens=p,
                completion_tokens=c,
                cost_usd=calc_cost_usd(model_key, p, c),
            )
        )
    return result


async def _top_users_since(session: AsyncSession, since: datetime, *, limit: int = 5) -> list[tuple[str, float, int]]:
    rows = (
        await session.execute(
            select(
                AiUsageLog.user_id,
                AiUsageLog.model_key,
                func.sum(AiUsageLog.prompt_tokens),
                func.sum(AiUsageLog.completion_tokens),
                func.count(AiUsageLog.id),
            )
            .where(AiUsageLog.created_at >= since, AiUsageLog.user_id.isnot(None))
            .group_by(AiUsageLog.user_id, AiUsageLog.model_key)
        )
    ).all()
    by_user: dict[int, tuple[float, int]] = {}
    for user_id, model_key, prompt, completion, req_count in rows:
        cost = calc_cost_usd(model_key, int(prompt or 0), int(completion or 0))
        prev_cost, prev_req = by_user.get(user_id, (0.0, 0))
        by_user[user_id] = (prev_cost + cost, prev_req + int(req_count or 0))

    if not by_user:
        return []

    top_ids = sorted(by_user.items(), key=lambda x: x[1][0], reverse=True)[:limit]
    user_ids = [uid for uid, _ in top_ids]
    users = {
        u.id: u
        for u in (await session.execute(select(User).where(User.id.in_(user_ids)))).scalars().all()
    }
    out: list[tuple[str, float, int]] = []
    for uid, (cost, req) in top_ids:
        u = users.get(uid)
        name = f"@{u.username}" if u and u.username else f"#{uid}"
        out.append((name, cost, req))
    return out


async def fetch_ai_cost_stats(session: AsyncSession) -> AiCostStats:
    today = _day_start()
    week = _utcnow() - timedelta(days=7)
    month = _utcnow() - timedelta(days=30)

    today_cost, today_requests = await _aggregate_since(session, today)
    week_cost, week_requests = await _aggregate_since(session, week)
    month_cost, month_requests = await _aggregate_since(session, month)
    total_cost, total_requests = await _aggregate_since(session, None)

    return AiCostStats(
        today_cost=today_cost,
        today_requests=today_requests,
        week_cost=week_cost,
        week_requests=week_requests,
        month_cost=month_cost,
        month_requests=month_requests,
        total_cost=total_cost,
        total_requests=total_requests,
        month_by_model=await _by_model_since(session, month),
        top_users_month=await _top_users_since(session, month),
        generated_at=_utcnow(),
    )


def format_ai_cost_stats_message(stats: AiCostStats, *, lang: str = "ru") -> str:
    from app.core.i18n import t

    lines = [
        t(lang, "admin_costs_title"),
        "",
        f"📅 {t(lang, 'admin_costs_today')}: <b>{format_usd(stats.today_cost)}</b> "
        f"({stats.today_requests} {t(lang, 'admin_costs_requests')})",
        f"📈 {t(lang, 'admin_costs_week')}: <b>{format_usd(stats.week_cost)}</b> "
        f"({stats.week_requests})",
        f"🗓 {t(lang, 'admin_costs_month')}: <b>{format_usd(stats.month_cost)}</b> "
        f"({stats.month_requests})",
        f"💰 {t(lang, 'admin_costs_total')}: <b>{format_usd(stats.total_cost)}</b> "
        f"({stats.total_requests})",
        "",
        t(lang, "admin_costs_by_model"),
    ]
    if stats.month_by_model:
        for row in stats.month_by_model:
            lines.append(
                t(
                    lang,
                    "admin_costs_model_line",
                    model=row.model_key,
                    cost=format_usd(row.cost_usd),
                    requests=row.requests,
                    inp=format_tokens(row.prompt_tokens),
                    out=format_tokens(row.completion_tokens),
                )
            )
    else:
        lines.append(t(lang, "admin_costs_no_data"))

    lines.extend(["", t(lang, "admin_costs_top_users")])
    if stats.top_users_month:
        for name, cost, req in stats.top_users_month:
            lines.append(
                t(lang, "admin_costs_user_line", user=name, cost=format_usd(cost), requests=req)
            )
    else:
        lines.append(t(lang, "admin_costs_no_data"))

    lines.extend(
        [
            "",
            t(lang, "admin_costs_rates"),
            "• gpt-4o-mini — $0.15 / $0.60",
            "• gpt-5.4-mini — $0.75 / $4.50",
            "• gpt-5.5 — $5.00 / $30.00",
            "",
            f"<i>{stats.generated_at.strftime('%d.%m.%Y %H:%M')} UTC</i>",
        ]
    )
    return "\n".join(lines)
