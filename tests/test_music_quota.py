import asyncio
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.entities import Base, User
from app.services.subscription_service import (
    check_music_quota,
    consume_music_operation,
    feature_allowed,
    module_allowed,
)


def _free_user_no_trial(**kwargs) -> User:
    """Free plan without signup Premium trial."""
    defaults = dict(
        id=1,
        telegram_id=1,
        plan_id="free",
        trial_expires_at=datetime(2000, 1, 1),
        ai_usage_month=datetime.utcnow().strftime("%Y-%m"),
    )
    defaults.update(kwargs)
    return User(**defaults)


def test_module_allowed_student_blocks_music():
    user = User(id=1, telegram_id=1, plan_id="student")
    assert module_allowed(user, "music") == "quota_student_module"


@pytest.mark.asyncio
async def test_check_music_quota_free_separate_blocked():
    async def _run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = _free_user_no_trial()
            session.add(user)
            await session.commit()
            msg = await check_music_quota(session, user, lang="ru", separate=True)
            assert msg is not None
            assert "Basic" in msg or "basic" in msg.lower() or "🎤" in msg
        await engine.dispose()

    await _run()


@pytest.mark.asyncio
async def test_consume_music_separate_increments_both_counters():
    async def _run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = User(
                id=1,
                telegram_id=1,
                plan_id="basic",
                ai_usage_month=datetime.utcnow().strftime("%Y-%m"),
            )
            session.add(user)
            await session.commit()
            await consume_music_operation(session, user, separate=True)
            await session.refresh(user)
            assert user.music_used_month == 1
            assert user.music_separate_used_month == 1
        await engine.dispose()

    await _run()


@pytest.mark.asyncio
async def test_check_music_quota_monthly_limit():
    async def _run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = _free_user_no_trial(music_used_month=3)
            session.add(user)
            await session.commit()
            msg = await check_music_quota(session, user, lang="ru", separate=False)
            assert msg is not None
            assert "3" in msg
        await engine.dispose()

    await _run()


def test_feature_allowed_pro_unlimited():
    user = User(id=1, telegram_id=1, plan_id="pro")
    assert feature_allowed(user, "music") is None
    assert feature_allowed(user, "music_separate") is None


def test_audio_ogg_document_mime():
    from app.services.music_service import audio_from_message

    class _Doc:
        file_id = "f1"
        mime_type = "application/ogg"
        file_name = "track.ogg"

    class _Msg:
        audio = None
        document = _Doc()
        voice = None

    assert audio_from_message(_Msg()) == ("f1", "track.ogg")
