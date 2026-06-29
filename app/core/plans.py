from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Official CBU rate, 24.06.2026 — https://www.cbu.uz
USD_TO_UZS = 12_017

PlanId = Literal["free", "basic", "premium", "pro", "student"]
PackageKind = Literal[
    "ai_credits",
    "image_gen",
    "photo_analysis",
    "memory_facts",
    "storage_mb",
]
AdvancedModelMode = Literal["none", "limited", "full", "router"]
ExportLevel = Literal["none", "pdf", "pdf_excel", "all"]

LEGACY_PLAN_ALIASES: dict[str, PlanId] = {"family": "premium"}


@dataclass(frozen=True)
class PlanLimits:
    ai_credits_monthly: int
    max_output_tokens: int
    photo_analysis_monthly: int | None
    image_gen_monthly: int | None
    pdf_docx_monthly: int | None
    memory_facts: int | None
    storage_mb: int
    vault_lock: bool
    reminders: int | None
    voice: bool
    ocr: bool
    doc_translate: bool
    advanced_model: AdvancedModelMode
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


STUDENT_MODULE_IDS: frozenset[str] = frozenset({"education", "ai_assistant", "vault", "organizer"})


PLANS: dict[PlanId, PlanInfo] = {
    "free": PlanInfo(
        id="free",
        emoji="🆓",
        usd_monthly=None,
        limits=PlanLimits(
            ai_credits_monthly=300,
            max_output_tokens=3000,
            photo_analysis_monthly=3,
            image_gen_monthly=0,
            pdf_docx_monthly=0,
            memory_facts=100,
            storage_mb=100,
            vault_lock=False,
            reminders=10,
            voice=False,
            ocr=False,
            doc_translate=False,
            advanced_model="none",
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
    "student": PlanInfo(
        id="student",
        emoji="🎓",
        usd_monthly=2.99,
        limits=PlanLimits(
            ai_credits_monthly=1500,
            max_output_tokens=4500,
            photo_analysis_monthly=50,
            image_gen_monthly=10,
            pdf_docx_monthly=20,
            memory_facts=1000,
            storage_mb=2048,
            vault_lock=True,
            reminders=20,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="limited",
            priority=False,
            max_priority=False,
            household_members=1,
            history_days=90,
            export_level="pdf",
            backup=False,
            workspaces=1,
            allowed_modules=STUDENT_MODULE_IDS,
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
        usd_monthly=5.99,
        limits=PlanLimits(
            ai_credits_monthly=5000,
            max_output_tokens=6500,
            photo_analysis_monthly=300,
            image_gen_monthly=40,
            pdf_docx_monthly=100,
            memory_facts=5000,
            storage_mb=10240,
            vault_lock=True,
            reminders=50,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="limited",
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
        usd_monthly=11.99,
        limits=PlanLimits(
            ai_credits_monthly=15000,
            max_output_tokens=10000,
            photo_analysis_monthly=1500,
            image_gen_monthly=120,
            pdf_docx_monthly=500,
            memory_facts=20000,
            storage_mb=51200,
            vault_lock=True,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="router",
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
        usd_monthly=19.99,
        limits=PlanLimits(
            ai_credits_monthly=40000,
            max_output_tokens=16000,
            photo_analysis_monthly=5000,
            image_gen_monthly=400,
            pdf_docx_monthly=2000,
            memory_facts=100000,
            storage_mb=204800,
            vault_lock=True,
            reminders=None,
            voice=True,
            ocr=True,
            doc_translate=True,
            advanced_model="router",
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
    AddonPackage("p_credits_500", "ai_credits", 500, 0.99, "plan_pkg_credits_500"),
    AddonPackage("p_credits_2000", "ai_credits", 2000, 2.99, "plan_pkg_credits_2000"),
    AddonPackage("p_credits_5000", "ai_credits", 5000, 5.99, "plan_pkg_credits_5000"),
    AddonPackage("p_credits_10000", "ai_credits", 10000, 9.99, "plan_pkg_credits_10000"),
)

AI_PACKAGES = ADDON_PACKAGES

TRIAL_DAYS = 3
REFERRAL_AI_BONUS = 100
WELCOME_AI_BONUS = 50
