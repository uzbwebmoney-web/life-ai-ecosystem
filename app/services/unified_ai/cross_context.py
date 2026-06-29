from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.ai_context import build_ai_memory_context
from app.services.ecosystem_service import unified_search
from app.services.health_service import list_health_medications
from app.services.household_service import effective_data_user_ids
from app.services.life_data import list_upcoming_reminders
from app.services.organizer_service import list_all_events, list_tasks
from app.core.i18n import t


async def build_cross_module_context(
    session: AsyncSession,
    user: User,
    modules: list[str],
    query: str,
    *,
    lang: str | None = None,
) -> str:
    lang = lang or user.language
    parts: list[str] = []
    mod_set = set(modules)

    if mod_set & {"health", "nutrition", "fitness"}:
        meds = await list_health_medications(session, user.id)
        if meds:
            parts.append(t(lang, "uni_ctx_meds") + ": " + ", ".join(m.name for m in meds[:5]))
        if "organizer" in mod_set or "health" in mod_set:
            events = await list_all_events(session, user.id, limit=3)
            visits = [e.title for e in events if e.event_type == "meeting"]
            if visits:
                parts.append(t(lang, "uni_ctx_visits") + ": " + ", ".join(visits))

    if mod_set & {"car", "finance", "travel"}:
        from app.services.life_profile_service import list_profile_facts

        facts = await list_profile_facts(session, user.id)
        car_facts = [f.fact_value for f in facts if f.category == "car"]
        if car_facts:
            parts.append(t(lang, "uni_ctx_car") + ": " + car_facts[0][:120])

    if mod_set & {"vault", "travel"}:
        hits = await unified_search(session, user, "паспорт passport", limit=2)
        if hits.records:
            parts.append(t(lang, "uni_ctx_passport") + ": " + hits.records[0].title)

    if mod_set & {"organizer", "finance", "travel"}:
        tasks = await list_tasks(session, user.id)
        open_tasks = [tk.title for tk in tasks if not tk.done][:4]
        if open_tasks:
            parts.append(t(lang, "uni_ctx_tasks") + ": " + ", ".join(open_tasks))

    user_ids = await effective_data_user_ids(session, user)
    for uid in user_ids[:1]:
        rems = await list_upcoming_reminders(session, uid, limit=3)
        if rems:
            parts.append(
                t(lang, "uni_ctx_reminders")
                + ": "
                + ", ".join(r.title for r in rems)
            )

    if not parts:
        return ""
    return t(lang, "uni_ctx_header") + "\n" + "\n".join(f"• {p}" for p in parts)


async def build_unified_ai_context(
    session: AsyncSession,
    user: User,
    query: str,
    modules: list[str],
) -> tuple[str, str, str]:
    profile_ctx, memory_ctx = await build_ai_memory_context(session, user, query)
    cross = await build_cross_module_context(session, user, modules, query, lang=user.language)
    combined_memory = memory_ctx
    if cross:
        combined_memory = f"{memory_ctx}\n\n{cross}".strip() if memory_ctx else cross
    return profile_ctx, combined_memory, cross


def unified_system_prompt(intent_modules: list[str], *, lang: str = "ru") -> str:
    from app.core.i18n import t

    mods = ", ".join(intent_modules)
    return t(lang, "uni_system_prompt", modules=mods)
