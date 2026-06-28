from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_pricing import (
    IMAGE_MODEL_KEY,
    ModelUsageRow,
    admin_rates_lines,
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


def _row_cost(
    model_key: str,
    prompt_tokens: int,
    completion_tokens: int,
    *,
    image_count: int = 0,
    image_quality: str | None = None,
) -> float:
    return calc_cost_usd(
        model_key,
        prompt_tokens,
        completion_tokens,
        image_count=image_count,
        image_quality=image_quality,
    )


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


async def record_image_usage(
    session: AsyncSession,
    user_id: int | None,
    model: str,
    *,
    quality: str,
    response=None,
) -> None:
    prompt_tokens, completion_tokens = extract_usage(response) if response else (0, 0)
    model_key = normalize_model_key(model)
    session.add(
        AiUsageLog(
            user_id=user_id,
            model=model,
            model_key=model_key,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            image_count=1,
            image_quality=quality,
            source="image_gen",
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
    month_images: int = 0
    month_image_cost: float = 0.0
    month_by_model: list[ModelUsageRow] = field(default_factory=list)
    top_users_month: list[tuple[str, float, int]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


async def _aggregate_since(session: AsyncSession, since: datetime | None) -> tuple[float, int]:
    q = select(
        AiUsageLog.model_key,
        func.coalesce(func.sum(AiUsageLog.prompt_tokens), 0),
        func.coalesce(func.sum(AiUsageLog.completion_tokens), 0),
        func.coalesce(func.sum(AiUsageLog.image_count), 0),
        AiUsageLog.image_quality,
        func.count(AiUsageLog.id),
    )
    if since is not None:
        q = q.where(AiUsageLog.created_at >= since)
    q = q.group_by(AiUsageLog.model_key, AiUsageLog.image_quality)
    rows = (await session.execute(q)).all()

    cost = 0.0
    total_requests = 0
    for model_key, prompt, completion, image_count, image_quality, count in rows:
        cost += _row_cost(
            model_key,
            int(prompt or 0),
            int(completion or 0),
            image_count=int(image_count or 0),
            image_quality=image_quality,
        )
        total_requests += int(count or 0)
    return cost, total_requests


async def _image_stats_since(session: AsyncSession, since: datetime) -> tuple[int, float]:
    rows = (
        await session.execute(
            select(
                AiUsageLog.image_quality,
                func.coalesce(func.sum(AiUsageLog.image_count), 0),
            )
            .where(AiUsageLog.created_at >= since, AiUsageLog.image_count > 0)
            .group_by(AiUsageLog.image_quality)
        )
    ).all()
    total_count = 0
    total_cost = 0.0
    for quality, count in rows:
        c = int(count or 0)
        total_count += c
        total_cost += _row_cost(IMAGE_MODEL_KEY, 0, 0, image_count=c, image_quality=quality)
    return total_count, total_cost


async def _by_model_since(session: AsyncSession, since: datetime) -> list[ModelUsageRow]:
    rows = (
        await session.execute(
            select(
                AiUsageLog.model_key,
                func.count(AiUsageLog.id),
                func.sum(AiUsageLog.prompt_tokens),
                func.sum(AiUsageLog.completion_tokens),
                func.sum(AiUsageLog.image_count),
                AiUsageLog.image_quality,
            )
            .where(AiUsageLog.created_at >= since)
            .group_by(AiUsageLog.model_key, AiUsageLog.image_quality)
            .order_by(func.count(AiUsageLog.id).desc())
        )
    ).all()
    result: list[ModelUsageRow] = []
    for model_key, requests, prompt, completion, image_count, image_quality in rows:
        p = int(prompt or 0)
        c = int(completion or 0)
        imgs = int(image_count or 0)
        result.append(
            ModelUsageRow(
                model_key=model_key,
                requests=int(requests or 0),
                prompt_tokens=p,
                completion_tokens=c,
                cost_usd=_row_cost(
                    model_key,
                    p,
                    c,
                    image_count=imgs,
                    image_quality=image_quality,
                ),
                image_count=imgs,
                image_quality=image_quality,
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
                func.sum(AiUsageLog.image_count),
                AiUsageLog.image_quality,
                func.count(AiUsageLog.id),
            )
            .where(AiUsageLog.created_at >= since, AiUsageLog.user_id.isnot(None))
            .group_by(AiUsageLog.user_id, AiUsageLog.model_key, AiUsageLog.image_quality)
        )
    ).all()
    by_user: dict[int, tuple[float, int]] = {}
    for user_id, model_key, prompt, completion, image_count, image_quality, req_count in rows:
        cost = _row_cost(
            model_key,
            int(prompt or 0),
            int(completion or 0),
            image_count=int(image_count or 0),
            image_quality=image_quality,
        )
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
    month_images, month_image_cost = await _image_stats_since(session, month)

    return AiCostStats(
        today_cost=today_cost,
        today_requests=today_requests,
        week_cost=week_cost,
        week_requests=week_requests,
        month_cost=month_cost,
        month_requests=month_requests,
        total_cost=total_cost,
        total_requests=total_requests,
        month_images=month_images,
        month_image_cost=month_image_cost,
        month_by_model=await _by_model_since(session, month),
        top_users_month=await _top_users_since(session, month),
        generated_at=_utcnow(),
    )


def _model_row_label(row: ModelUsageRow) -> str:
    if row.model_key == IMAGE_MODEL_KEY and row.image_count > 0:
        q = (row.image_quality or "medium").capitalize()
        return f"{row.model_key} ({q})"
    return row.model_key


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
    ]
    if stats.month_images:
        lines.append(
            t(
                lang,
                "admin_costs_images_month",
                count=stats.month_images,
                cost=format_usd(stats.month_image_cost),
            )
        )
    lines.extend(["", t(lang, "admin_costs_by_model")])
    if stats.month_by_model:
        for row in stats.month_by_model:
            if row.model_key == IMAGE_MODEL_KEY and row.image_count > 0:
                lines.append(
                    t(
                        lang,
                        "admin_costs_image_line",
                        model=_model_row_label(row),
                        cost=format_usd(row.cost_usd),
                        count=row.image_count,
                        requests=row.requests,
                    )
                )
            else:
                lines.append(
                    t(
                        lang,
                        "admin_costs_model_line",
                        model=_model_row_label(row),
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

    lines.extend(["", t(lang, "admin_costs_rates")])
    lines.extend(admin_rates_lines())
    lines.extend(["", f"<i>{stats.generated_at.strftime('%d.%m.%Y %H:%M')} UTC</i>"])
    return "\n".join(lines)
