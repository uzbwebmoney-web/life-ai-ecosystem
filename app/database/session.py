from sqlalchemy import inspect, text

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine



from app.core.config import settings

from app.models.entities import Base



engine = create_async_engine(settings.database_url, echo=False)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



_EXTRA_COLUMNS: dict[str, dict[str, str]] = {

    "users": {

        "voice_mode": "BOOLEAN DEFAULT 0",

        "utc_offset_minutes": "INTEGER DEFAULT 300",

        "active_module_id": "VARCHAR(32)",

        "active_submodule_id": "VARCHAR(32)",

        "onboarding_done": "BOOLEAN DEFAULT 0",

        "welcome_pending": "BOOLEAN DEFAULT 0",

        "household_id": "INTEGER",

        "last_daily_feed_date": "VARCHAR(10)",

        "vault_password_hash": "VARCHAR(255)",

        "plan_id": "VARCHAR(16) DEFAULT 'free'",

        "plan_expires_at": "DATETIME",

        "trial_expires_at": "DATETIME",

        "ai_bonus_balance": "INTEGER DEFAULT 0",

        "ai_used_today": "INTEGER DEFAULT 0",

        "ai_used_month": "INTEGER DEFAULT 0",

        "ai_usage_day": "VARCHAR(10)",

        "ai_usage_month": "VARCHAR(7)",

        "referral_code": "VARCHAR(16)",

        "referred_by_user_id": "INTEGER",

        "photo_used_month": "INTEGER DEFAULT 0",

        "music_used_month": "INTEGER DEFAULT 0",

        "music_separate_used_month": "INTEGER DEFAULT 0",

        "image_gen_used_month": "INTEGER DEFAULT 0",

        "pdf_used_month": "INTEGER DEFAULT 0",

        "advanced_model_used_month": "INTEGER DEFAULT 0",
        "pro_model_used_month": "INTEGER DEFAULT 0",

        "bonus_photo_analysis": "INTEGER DEFAULT 0",

        "bonus_image_gen": "INTEGER DEFAULT 0",

        "bonus_advanced_model": "INTEGER DEFAULT 0",

        "bonus_pro_model": "INTEGER DEFAULT 0",

        "bonus_memory_facts": "INTEGER DEFAULT 0",

        "bonus_storage_mb": "INTEGER DEFAULT 0",

        "vault_unlocked_until": "DATETIME",

        "ui_mode": "VARCHAR(16) DEFAULT 'normal'",

        "response_style": "VARCHAR(32) DEFAULT 'balanced'",

        "knowledge_level": "VARCHAR(16) DEFAULT 'standard'",

        "active_project_id": "INTEGER",

        "last_evening_feed_date": "VARCHAR(10)",

        "agent_mode": "VARCHAR(16) DEFAULT 'auto'",

    },

    "calendar_events": {

        "recurrence": "VARCHAR(16) DEFAULT ''",

        "household_id": "INTEGER",

        "shared": "BOOLEAN DEFAULT 0",

    },

    "credit_loans": {

        "remaining_amount": "FLOAT",

    },

    "alert_items": {

        "notes": "TEXT DEFAULT ''",

        "remind_before_minutes": "INTEGER DEFAULT 0",

        "sent": "BOOLEAN DEFAULT 0",

    },

    "health_medications": {

        "snooze_until": "DATETIME",

    },

    "ai_usage_logs": {
        "image_count": "INTEGER DEFAULT 0",
        "image_quality": "VARCHAR(16)",
    },

}





async def _migrate_sqlite_columns() -> None:

    if not settings.database_url.startswith("sqlite"):

        return

    async with engine.begin() as conn:

        def _run(sync_conn):

            insp = inspect(sync_conn)

            for table, columns in _EXTRA_COLUMNS.items():

                if not insp.has_table(table):

                    continue

                existing = {c["name"] for c in insp.get_columns(table)}

                for col, ddl in columns.items():

                    if col not in existing:

                        sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))



        await conn.run_sync(_run)





async def init_db() -> None:

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

    await _migrate_sqlite_columns()

    async with engine.begin() as conn:

        await conn.execute(

            text(

                "UPDATE credit_loans SET remaining_amount = total_amount "

                "WHERE remaining_amount IS NULL"

            )

        )

