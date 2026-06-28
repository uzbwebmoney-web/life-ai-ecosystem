from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Official CBU rate, 24.06.2026 — https://www.cbu.uz
USD_TO_UZS = 12_017

PlanId = Literal["free", "basic", "premium", "pro", "student"]
PackageKind = Literal["ai_requests", "image_gen", "photo_analysis", "memory_facts", "storage_mb"]
AdvancedModelMode = Literal["none", "limited", "full", "router"]
ExportLevel = Literal["none", "pdf", "pdf_excel", "all"]

# Legacy paid plan id → current plan
LEGACY_PLAN_ALIASES: dict[str, PlanId] = {"family": "premium"}


@dataclass(frozen=True)
class PlanLimits:
    ai_daily: int | None
    ai_monthly: int | None
    photo_analysis_monthly: int | None  # None = unlimited, 0 = disabled
    image_gen_monthly: int | None
    pdf_docx_monthly: int | None
    memory_facts: int | None
    storage_mb: int
    reminders: int | None
    voice: bool
    ocr: bool
    doc_translate: bool
    advanced_model: AdvancedModelMode
    advanced_model_monthly: int | None
    priority: bool
    max_priority: bool
    household_members: int
    history_days: int | None
    export_level: ExportLevel
    backup: bool
    workspaces: int
    allowed_modules: frozenset[str] | None
    cars: int
    health_profiles: int
    family_profiles: int

    @property
    def photo_ai(self) -> bool:
        return self.photo_analysis_monthly != 0


@dataclass(frozen=True)
class PlanInfo:
    id: PlanId
    emoji: str
    usd_monthly: float | None
    limits: PlanLimits
    name_key: str
    desc_key: str


@dataclass(frozen=True)
class AddonPackage:
    id: str
    kind: PackageKind
    amount: int
    usd_price: float
    name_key: str


def normalize_plan_id(plan_id: str) -> str:
    return LEGACY_PLAN_ALIASES.get(plan_id, plan_id)


def usd_to_uzs(usd: float) -> int:
    return int(round(usd * USD_TO_UZS / 1000) * 1000)


USD_TO_STARS = 75


def usd_to_stars(usd: float) -> int:
    return max(1, int(round(usd * USD_TO_STARS / 50) * 50))


def format_uzs(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def format_stars(amount: int) -> str:
    return f"{amount} ⭐"


PLANS: dict[PlanId, PlanInfo] = {
    "free": PlanInfo(
        id="free",
        emoji="🆓",
        usd_monthly=None,
        limits=PlanLimits(
            ai_daily=20,
            ai_monthly=None,
            photo_analysis_monthly=5,
            image_gen_monthly=0,
            pdf_docx_monthly=0,
            memory_facts=100,
            storage_mb=100,
            reminders=10,
            voice=False,
            ocr=False,
            doc_translate=False,
            advanced_model="none",
            advanced_model_monthly=None,
            priority=False,
            max_priority=False,
            household_members=1,
            history_days=30,
            export_level="none",
            backup=False,
            workspaces=1,
            allowed_modules=None,
            cars=1,
            health_profiles=1,
            family_profiles=1,
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
            ai_monthly=500,
            photo_analysis_monthly=100,
            image_gen_monthly=20,
            pdf_docx_monthly=20,
            memory_facts=1000,
            storage_mb=2048,
            reminders=50,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="limited",
            advanced_model_monthly=50,
            priority=False,
            max_priority=False,
            household_members=1,
            history_days=180,
            export_level="pdf",
            backup=True,
            workspaces=1,
            allowed_modules=None,
            cars=2,
            health_profiles=2,
            family_profiles=2,
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
            ai_monthly=3000,
            photo_analysis_monthly=None,
            image_gen_monthly=100,
            pdf_docx_monthly=None,
            memory_facts=10_000,
            storage_mb=20_480,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="full",
            advanced_model_monthly=None,
            priority=True,
            max_priority=False,
            household_members=5,
            history_days=730,
            export_level="pdf_excel",
            backup=True,
            workspaces=2,
            allowed_modules=None,
            cars=5,
            health_profiles=5,
            family_profiles=5,
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
            photo_analysis_monthly=None,
            image_gen_monthly=500,
            pdf_docx_monthly=None,
            memory_facts=None,
            storage_mb=102_400,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="router",
            advanced_model_monthly=None,
            priority=True,
            max_priority=True,
            household_members=10,
            history_days=None,
            export_level="all",
            backup=True,
            workspaces=5,
            allowed_modules=None,
            cars=99,
            health_profiles=99,
            family_profiles=99,
        ),
        name_key="plan_pro_name",
        desc_key="plan_pro_desc",
    ),
    "student": PlanInfo(
        id="student",
        emoji="🎓",
        usd_monthly=2.49,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=300,
            photo_analysis_monthly=30,
            image_gen_monthly=0,
            pdf_docx_monthly=50,
            memory_facts=500,
            storage_mb=512,
            reminders=20,
            voice=False,
            ocr=True,
            doc_translate=True,
            advanced_model="none",
            advanced_model_monthly=None,
            priority=False,
            max_priority=False,
            household_members=1,
            history_days=90,
            export_level="pdf",
            backup=False,
            workspaces=1,
            allowed_modules=frozenset({"education", "ai_assistant", "vault", "organizer"}),
            cars=1,
            health_profiles=1,
            family_profiles=1,
        ),
        name_key="plan_student_name",
        desc_key="plan_student_desc",
    ),
}

ADDON_PACKAGES: tuple[AddonPackage, ...] = (
    AddonPackage("p100", "ai_requests", 100, 2.0, "plan_pkg_100"),
    AddonPackage("p500", "ai_requests", 500, 7.0, "plan_pkg_500"),
    AddonPackage("p1000", "ai_requests", 1000, 12.0, "plan_pkg_1000"),
    AddonPackage("p_img100", "image_gen", 100, 3.0, "plan_pkg_img100"),
    AddonPackage("p_photo500", "photo_analysis", 500, 5.0, "plan_pkg_photo500"),
    AddonPackage("p_mem10k", "memory_facts", 10_000, 2.0, "plan_pkg_mem10k"),
    AddonPackage("p_cloud50", "storage_mb", 51_200, 5.0, "plan_pkg_cloud50"),
)

# Backward-compatible alias
AI_PACKAGES = ADDON_PACKAGES

TRIAL_DAYS = 3
REFERRAL_AI_BONUS = 100
WELCOME_AI_BONUS = 50

STUDENT_MODULE_IDS: frozenset[str] = frozenset({"education", "ai_assistant", "vault", "organizer"})
