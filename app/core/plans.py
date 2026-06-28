from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Official CBU rate, 24.06.2026 — https://www.cbu.uz
USD_TO_UZS = 12_017

PlanId = Literal["free", "basic", "premium", "pro", "family"]


@dataclass(frozen=True)
class PlanLimits:
    ai_daily: int | None
    ai_monthly: int | None
    reminders: int | None
    cars: int
    health_profiles: int
    family_profiles: int
    storage_mb: int
    memory_facts: int | None
    voice: bool
    photo_ai: bool
    priority: bool
    premium_model: bool
    household_members: int


@dataclass(frozen=True)
class PlanInfo:
    id: PlanId
    emoji: str
    usd_monthly: float | None
    limits: PlanLimits
    name_key: str
    desc_key: str


@dataclass(frozen=True)
class AiPackage:
    id: str
    requests: int
    usd_price: float
    name_key: str


def usd_to_uzs(usd: float) -> int:
    return int(round(usd * USD_TO_UZS / 1000) * 1000)


def format_uzs(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


PLANS: dict[PlanId, PlanInfo] = {
    "free": PlanInfo(
        id="free",
        emoji="🆓",
        usd_monthly=None,
        limits=PlanLimits(
            ai_daily=20,
            ai_monthly=None,
            reminders=5,
            cars=1,
            health_profiles=1,
            family_profiles=1,
            storage_mb=100,
            memory_facts=20,
            voice=False,
            photo_ai=False,
            priority=False,
            premium_model=False,
            household_members=1,
        ),
        name_key="plan_free_name",
        desc_key="plan_free_desc",
    ),
    "basic": PlanInfo(
        id="basic",
        emoji="🥉",
        usd_monthly=4.0,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=400,
            reminders=50,
            cars=2,
            health_profiles=2,
            family_profiles=2,
            storage_mb=2048,
            memory_facts=200,
            voice=True,
            photo_ai=True,
            priority=True,
            premium_model=False,
            household_members=2,
        ),
        name_key="plan_basic_name",
        desc_key="plan_basic_desc",
    ),
    "premium": PlanInfo(
        id="premium",
        emoji="🥈",
        usd_monthly=9.0,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=2000,
            reminders=None,
            cars=5,
            health_profiles=5,
            family_profiles=5,
            storage_mb=20_480,
            memory_facts=1000,
            voice=True,
            photo_ai=True,
            priority=True,
            premium_model=False,
            household_members=4,
        ),
        name_key="plan_premium_name",
        desc_key="plan_premium_desc",
    ),
    "pro": PlanInfo(
        id="pro",
        emoji="🥇",
        usd_monthly=17.0,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=999_999,
            reminders=None,
            cars=99,
            health_profiles=99,
            family_profiles=99,
            storage_mb=102_400,
            memory_facts=None,
            voice=True,
            photo_ai=True,
            priority=True,
            premium_model=True,
            household_members=10,
        ),
        name_key="plan_pro_name",
        desc_key="plan_pro_desc",
    ),
    "family": PlanInfo(
        id="family",
        emoji="💼",
        usd_monthly=25.0,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=3000,
            reminders=None,
            cars=10,
            health_profiles=10,
            family_profiles=10,
            storage_mb=51_200,
            memory_facts=1000,
            voice=True,
            photo_ai=True,
            priority=True,
            premium_model=False,
            household_members=5,
        ),
        name_key="plan_family_name",
        desc_key="plan_family_desc",
    ),
}

AI_PACKAGES: tuple[AiPackage, ...] = (
    AiPackage("p100", 100, 2.0, "plan_pkg_100"),
    AiPackage("p500", 500, 7.0, "plan_pkg_500"),
    AiPackage("p1000", 1000, 12.0, "plan_pkg_1000"),
)

TRIAL_DAYS = 7
REFERRAL_AI_BONUS = 100
WELCOME_AI_BONUS = 50
