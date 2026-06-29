import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.entities import Base, ProcessedStarsPayment, User
from app.services.payment_service import activate_product_purchase, register_stars_payment


def test_register_stars_payment_idempotent():
    async def _run():
        from sqlalchemy import select

        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            user = User(id=1, telegram_id=1, plan_id="free")
            session.add(user)
            await session.commit()

            assert await register_stars_payment(
                session,
                charge_id="chg_1",
                user_id=1,
                product_type="package",
                product_id="p_credits_500",
            )
            assert not await register_stars_payment(
                session,
                charge_id="chg_1",
                user_id=1,
                product_type="package",
                product_id="p_credits_500",
            )

            await activate_product_purchase(session, user, "package", "p_credits_500")
            await session.refresh(user)
            assert user.ai_bonus_balance == 500

            rows = (await session.execute(select(ProcessedStarsPayment))).scalars().all()
            assert len(rows) == 1
        await engine.dispose()

    asyncio.run(_run())
