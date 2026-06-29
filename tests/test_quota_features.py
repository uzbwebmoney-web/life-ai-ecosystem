import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.entities import Base, LifeRecord, User
from app.services.subscription_service import (
    QUOTA_BLOCK_PREFIX,
    check_export_allowed,
    check_model_quota,
    consume_ai_request,
    feature_allowed,
    parse_insufficient_credits_reply,
)
from app.services.vault_expiry_service import merge_meta_expiry, parse_meta_expiry, schedule_vault_expiry_alert


def test_check_model_quota_blocks_free_advanced():
    user = User(id=1, telegram_id=1, plan_id="free")
    msg = check_model_quota(user, settings.effective_advanced_model, lang="ru")
    assert msg is not None
    assert msg.startswith(QUOTA_BLOCK_PREFIX)
    is_quota, body = parse_insufficient_credits_reply(msg)
    assert is_quota
    assert "GPT-5.4" in body


def test_check_model_quota_allows_base():
    user = User(id=1, telegram_id=1, plan_id="free")
    assert check_model_quota(user, settings.openai_model, lang="ru") is None


def test_consume_ai_request_tracks_advanced():
    async def _run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = User(id=1, telegram_id=1, plan_id="basic", ai_usage_month=datetime.utcnow().strftime("%Y-%m"))
            session.add(user)
            await session.commit()
            await consume_ai_request(session, user, credits=2, model=settings.effective_advanced_model)
            await session.refresh(user)
            assert user.advanced_model_used_month == 1
        await engine.dispose()

    asyncio.run(_run())


def test_check_export_allowed_free():
    user = User(id=1, telegram_id=1, plan_id="free")
    assert check_export_allowed(user, lang="ru") is not None


def test_merge_meta_expiry_roundtrip():
    exp = datetime(2030, 12, 31, 12, 0, 0)
    meta = merge_meta_expiry('{"telegram_file_id":"x"}', exp)
    assert parse_meta_expiry(meta) is not None


def test_schedule_vault_expiry_alert():
    async def _run():
        from sqlalchemy import select

        from app.models.entities import AlertItem

        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = User(id=1, telegram_id=1, plan_id="student")
            session.add(user)
            await session.commit()
            record = LifeRecord(
                id=1,
                user_id=1,
                module_id="vault",
                submodule_id="passport",
                title="Passport",
                body="tags",
            )
            session.add(record)
            await session.commit()
            await schedule_vault_expiry_alert(
                session,
                user_id=1,
                record=record,
                expires_at=datetime.utcnow() + timedelta(days=90),
                lang="ru",
            )
            rows = (await session.execute(select(AlertItem).where(AlertItem.user_id == 1))).scalars().all()
            assert len(rows) >= 1
            assert any("vault:1" in (a.notes or "") for a in rows)
        await engine.dispose()

    asyncio.run(_run())


def test_feature_allowed_music_free_has_teaser():
    user = User(id=1, telegram_id=1, plan_id="free")
    assert feature_allowed(user, "music") is None
    assert feature_allowed(user, "music_separate") == "quota_music_separate"


def test_feature_allowed_music_student_blocked():
    user = User(id=1, telegram_id=1, plan_id="student")
    assert feature_allowed(user, "music") == "quota_music"


def test_feature_allowed_music_basic():
    user = User(id=1, telegram_id=1, plan_id="basic")
    assert feature_allowed(user, "music") is None
    assert feature_allowed(user, "music_separate") is None


def test_feature_allowed_ocr_free():
    user = User(id=1, telegram_id=1, plan_id="free")
    assert feature_allowed(user, "ocr") == "quota_ocr"
