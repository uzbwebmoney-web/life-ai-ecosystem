from __future__ import annotations

import re
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import HealthMedication, HealthMetric, Reminder, User

METRIC_PRESSURE = "pressure"
METRIC_SUGAR = "sugar"
METRIC_WEIGHT = "weight"
METRIC_OTHER = "other"

HEALTH_VISIT_MODULE = "health"
HEALTH_VISIT_SUB = "visits"
HEALTH_DOC_SUB = "documents"

_TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def user_local_now(user: User, now: datetime | None = None) -> datetime:
    now = now or datetime.utcnow()
    return now + timedelta(minutes=int(user.utc_offset_minutes or 0))


def parse_reminder_times(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    valid: list[str] = []
    for part in parts:
        if _TIME_RE.match(part):
            h, m = part.split(":")
            valid.append(f"{int(h):02d}:{m}")
    return sorted(set(valid))


def parse_pressure(raw: str) -> tuple[float, float] | None:
    cleaned = raw.strip().replace(" ", "")
    if "/" in cleaned:
        a, b = cleaned.split("/", 1)
        try:
            return float(a.replace(",", ".")), float(b.replace(",", "."))
        except ValueError:
            return None
    return None


def parse_single_value(raw: str) -> float | None:
    try:
        return float(raw.strip().replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


def metric_unit(metric_type: str) -> str:
    return {
        METRIC_PRESSURE: "mmHg",
        METRIC_SUGAR: "mmol/L",
        METRIC_WEIGHT: "kg",
    }.get(metric_type, "")


async def add_health_metric(
    session: AsyncSession,
    *,
    user_id: int,
    metric_type: str,
    value_primary: float,
    value_secondary: float | None = None,
    notes: str = "",
    profile_id: int | None = None,
    recorded_at: datetime | None = None,
) -> HealthMetric:
    row = HealthMetric(
        user_id=user_id,
        profile_id=profile_id,
        metric_type=metric_type,
        value_primary=value_primary,
        value_secondary=value_secondary,
        unit=metric_unit(metric_type),
        notes=notes.strip()[:2000],
        recorded_at=recorded_at or datetime.utcnow(),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def list_health_metrics(
    session: AsyncSession,
    user_id: int,
    *,
    metric_type: str | None = None,
    limit: int = 15,
) -> list[HealthMetric]:
    query = select(HealthMetric).where(HealthMetric.user_id == user_id)
    if metric_type:
        query = query.where(HealthMetric.metric_type == metric_type)
    rows = (
        await session.execute(query.order_by(HealthMetric.recorded_at.desc(), HealthMetric.id.desc()).limit(limit))
    ).scalars().all()
    return list(rows)


async def add_health_medication(
    session: AsyncSession,
    *,
    user_id: int,
    name: str,
    dosage: str,
    reminder_times: str,
    profile_id: int | None = None,
) -> HealthMedication:
    times = parse_reminder_times(reminder_times)
    if not times:
        raise ValueError("invalid_times")
    med = HealthMedication(
        user_id=user_id,
        profile_id=profile_id,
        name=name.strip()[:255],
        dosage=dosage.strip()[:128],
        reminder_times=",".join(times),
    )
    session.add(med)
    await session.commit()
    await session.refresh(med)
    return med


async def list_health_medications(session: AsyncSession, user_id: int, *, active_only: bool = True) -> list[HealthMedication]:
    query = select(HealthMedication).where(HealthMedication.user_id == user_id)
    if active_only:
        query = query.where(HealthMedication.active.is_(True))
    rows = (await session.execute(query.order_by(HealthMedication.id.asc()))).scalars().all()
    return list(rows)


async def deactivate_health_medication(session: AsyncSession, user_id: int, med_id: int) -> bool:
    med = (
        await session.execute(
            select(HealthMedication).where(
                HealthMedication.id == med_id,
                HealthMedication.user_id == user_id,
                HealthMedication.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not med:
        return False
    med.active = False
    await session.commit()
    return True


async def get_health_medication(session: AsyncSession, user_id: int, med_id: int) -> HealthMedication | None:
    return (
        await session.execute(
            select(HealthMedication).where(
                HealthMedication.id == med_id,
                HealthMedication.user_id == user_id,
                HealthMedication.active.is_(True),
            )
        )
    ).scalar_one_or_none()


async def update_health_medication(
    session: AsyncSession,
    user_id: int,
    med_id: int,
    *,
    name: str | None = None,
    dosage: str | None = None,
    reminder_times: str | None = None,
) -> HealthMedication | None:
    med = await get_health_medication(session, user_id, med_id)
    if not med:
        return None
    if name is not None:
        med.name = name.strip()[:255]
    if dosage is not None:
        med.dosage = dosage.strip()[:128]
    if reminder_times is not None:
        times = parse_reminder_times(reminder_times)
        if not times:
            raise ValueError("invalid_times")
        med.reminder_times = ",".join(times)
        med.last_notified_key = None
    await session.commit()
    await session.refresh(med)
    return med


async def list_health_visits(session: AsyncSession, user_id: int, *, limit: int = 10) -> list[Reminder]:
    rows = (
        await session.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.module_id == HEALTH_VISIT_MODULE,
                Reminder.sent.is_(False),
                Reminder.due_at >= datetime.utcnow(),
            )
            .order_by(Reminder.due_at.asc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


def format_metric_line(metric: HealthMetric, lang: str = "ru") -> str:
    ts = metric.recorded_at.strftime("%d.%m.%Y %H:%M")
    if metric.metric_type == METRIC_PRESSURE and metric.value_secondary is not None:
        value = f"{int(metric.value_primary)}/{int(metric.value_secondary)} {metric.unit}"
    else:
        val = int(metric.value_primary) if float(metric.value_primary).is_integer() else metric.value_primary
        value = f"{val} {metric.unit}".strip()
    label = t(lang, f"health_metric_{metric.metric_type}")
    line = f"• <b>{label}</b>: {value} <i>({ts})</i>"
    if metric.notes:
        line += f"\n  <i>{metric.notes[:120]}</i>"
    return line


def format_medication_line(med: HealthMedication, lang: str = "ru") -> str:
    times = med.reminder_times.replace(",", ", ")
    return (
        f"• <b>{med.name}</b>\n"
        f"  {t(lang, 'health_med_dose')}: {med.dosage or '—'}\n"
        f"  🕐 {times}"
    )


def build_med_reminder_text(med: HealthMedication, lang: str = "ru") -> str:
    return (
        f"💊 <b>{t(lang, 'health_med_reminder_title')}</b>\n\n"
        f"{med.name}\n"
        f"{t(lang, 'health_med_dose')}: {med.dosage or '—'}"
    )


def _notify_key(med_id: int, local_dt: datetime, time_str: str) -> str:
    return f"{med_id}:{local_dt.strftime('%Y-%m-%d')}:{time_str}"


async def fetch_med_reminders_due(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[tuple[HealthMedication, User, str]]:
    now = now or datetime.utcnow()
    rows = (
        await session.execute(
            select(HealthMedication, User)
            .join(User, User.id == HealthMedication.user_id)
            .where(HealthMedication.active.is_(True))
        )
    ).all()
    due: list[tuple[HealthMedication, User, str]] = []
    for med, user in rows:
        local = user_local_now(user, now)
        current_time = local.strftime("%H:%M")
        for time_str in med.reminder_times.split(","):
            if time_str != current_time:
                continue
            key = _notify_key(med.id, local, time_str)
            if med.last_notified_key == key:
                continue
            due.append((med, user, key))
    return due


async def list_health_documents(session: AsyncSession, user_id: int, *, limit: int = 10) -> list:
    from app.models.entities import LifeRecord

    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == "health",
                LifeRecord.submodule_id == HEALTH_DOC_SUB,
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


HEALTH_SUBMODULE_AI: dict[str, str] = {
    "consultant": "Ты медицинский AI-консультант. Помогай разобрать симптомы: возможные причины, на что обратить внимание, когда срочно к врачу. Не ставь диагноз.",
    "symptoms": "Разбирай симптомы пользователя структурированно: что может означать, красные флаги, рекомендации по обращению к врачу.",
    "tests": "Объясняй результаты лабораторных анализов простым языком: что показывает показатель, нормы (общие), что обсудить с врачом.",
    "exams": "Объясняй результаты обследований (УЗИ, МРТ, КТ, рентген, ЭКГ и др.) понятным языком без диагноза.",
    "medicines": "Давай справочную информацию о лекарствах: назначение, типичные дозировки, побочные эффекты, взаимодействия. Напоминай, что назначение только врач.",
}


def health_submodule_description(sub_id: str, lang: str) -> str:
    key = f"health_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else t(lang, "health_ai_hint")


async def mark_med_notified(session: AsyncSession, med_id: int, notify_key: str) -> None:
    await session.execute(
        update(HealthMedication).where(HealthMedication.id == med_id).values(last_notified_key=notify_key)
    )
    await session.commit()
