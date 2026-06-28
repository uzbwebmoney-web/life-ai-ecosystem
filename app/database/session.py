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

    },

    "calendar_events": {

        "recurrence": "VARCHAR(16) DEFAULT ''",

    },

    "credit_loans": {

        "remaining_amount": "FLOAT",

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

