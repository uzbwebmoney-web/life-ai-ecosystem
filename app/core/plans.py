from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Official CBU rate, 24.06.2026 — https://www.cbu.uz
USD_TO_UZS = 12_017

PlanId = Literal["free", "basic", "premium", "pro", "student"]
PackageKind = Literal[
    "ai_requests",
    "image_gen",
    "photo_analysis",
    "memory_facts",
    "storage_mb",
    "advanced_ai",
    "pro_ai",
]
AdvancedModelMode = Literal["none", "limited", "full", "router"]
ExportLevel = Literal["none", "pdf", "pdf_excel", "all"]

LEGACY_PLAN_ALIASES: dict[str, PlanId] = {"family": "premium"}

# Internal AI-request weights (not shown to users)
AI_REQUEST_WEIGHT: dict[str, int] = {
    "gpt-4o-mini": 1,
    "gpt-5.4-mini": 5,
    "gpt-5.5": 20,
}


@dataclass(frozen=True)
class PlanLimits:
    ai_daily: int | None
    ai_monthly: int | None
    photo_analysis_monthly: int | None
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
    pro_model_monthly: int | None
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


def ai_request_weight(model: str) -> int:
    from app.core.ai_pricing import normalize_model_key

    key = normalize_model_key(model)
    return AI_REQUEST_WEIGHT.get(key, 1)


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
            pdf_docx_monthly=3,
            memory_facts=100,
            storage_mb=100,
            reminders=10,
            voice=False,
            ocr=False,
            doc_translate=False,
            advanced_model="none",
            advanced_model_monthly=0,
            pro_model_monthly=0,
            priority=False,
            max_priority=False,
            household_members=1,
            history_days=30,
            export_level="pdf",
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
    "student": PlanInfo(
        id="student",
        emoji="🎓",
        usd_monthly=2.99,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=None,
            photo_analysis_monthly=50,
            image_gen_monthly=5,
            pdf_docx_monthly=20,
            memory_facts=500,
            storage_mb=1024,
            reminders=20,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="limited",
            advanced_model_monthly=50,
            pro_model_monthly=0,
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
    "basic": PlanInfo(
        id="basic",
        emoji="🥉",
        usd_monthly=7.99,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=None,
            photo_analysis_monthly=300,
            image_gen_monthly=30,
            pdf_docx_monthly=100,
            memory_facts=2000,
            storage_mb=5120,
            reminders=50,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="limited",
            advanced_model_monthly=300,
            pro_model_monthly=0,
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
        usd_monthly=14.99,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=None,
            photo_analysis_monthly=1500,
            image_gen_monthly=100,
            pdf_docx_monthly=500,
            memory_facts=10_000,
            storage_mb=20_480,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="router",
            advanced_model_monthly=1500,
            pro_model_monthly=30,
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
        usd_monthly=29.99,
        limits=PlanLimits(
            ai_daily=None,
            ai_monthly=None,
            photo_analysis_monthly=5000,
            image_gen_monthly=500,
            pdf_docx_monthly=2000,
            memory_facts=50_000,
            storage_mb=102_400,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="router",
            advanced_model_monthly=5000,
            pro_model_monthly=300,
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
}

ADDON_PACKAGES: tuple[AddonPackage, ...] = (
    AddonPackage("p_img50", "image_gen", 50, 4.99, "plan_pkg_img50"),
    AddonPackage("p_gpt54_500", "advanced_ai", 500, 4.99, "plan_pkg_gpt54_500"),
    AddonPackage("p_gpt55_50", "pro_ai", 50, 9.99, "plan_pkg_gpt55_50"),
    AddonPackage("p_cloud20", "storage_mb", 20_480, 2.99, "plan_pkg_cloud20"),
)

AI_PACKAGES = ADDON_PACKAGES

TRIAL_DAYS = 3
REFERRAL_AI_BONUS = 50
WELCOME_AI_BONUS = 20

STUDENT_MODULE_IDS: frozenset[str] = frozenset({"education", "ai_assistant", "vault", "organizer"})
