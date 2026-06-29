from __future__ import annotations

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Household, HouseholdMember, User


def _new_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def get_or_create_household(session: AsyncSession, owner: User) -> Household:
    if owner.household_id:
        row = (
            await session.execute(select(Household).where(Household.id == owner.household_id))
        ).scalar_one_or_none()
        if row:
            return row
    household = Household(owner_user_id=owner.id, invite_code=_new_code())
    session.add(household)
    await session.flush()
    owner.household_id = household.id
    member = HouseholdMember(household_id=household.id, user_id=owner.id, role="owner")
    session.add(member)
    await session.commit()
    await session.refresh(household)
    return household


async def join_household(session: AsyncSession, user: User, code: str) -> tuple[bool, str]:
    code = code.strip().upper()
    household = (
        await session.execute(select(Household).where(Household.invite_code == code))
    ).scalar_one_or_none()
    if not household:
        return False, "not_found"
    existing = (
        await session.execute(select(HouseholdMember).where(HouseholdMember.user_id == user.id))
    ).scalar_one_or_none()
    if existing:
        return False, "already"
    members = await get_household_members(session, household.id)
    owner = (
        await session.execute(select(User).where(User.id == household.owner_user_id))
    ).scalar_one_or_none()
    if owner:
        from app.services.subscription_service import plan_info

        limit = plan_info(owner).limits.household_members
        if len(members) >= limit:
            return False, "full"
    session.add(HouseholdMember(household_id=household.id, user_id=user.id, role="member"))
    user.household_id = household.id
    await session.commit()
    return True, "ok"


async def get_household_members(session: AsyncSession, household_id: int) -> list[HouseholdMember]:
    rows = (
        await session.execute(select(HouseholdMember).where(HouseholdMember.household_id == household_id))
    ).scalars().all()
    return list(rows)


async def get_household_member_user_ids(session: AsyncSession, user: User) -> list[int]:
    if not user.household_id:
        return [user.id]
    members = await get_household_members(session, user.household_id)
    ids = {user.id}
    for member in members:
        ids.add(member.user_id)
    household = (
        await session.execute(select(Household).where(Household.id == user.household_id))
    ).scalar_one_or_none()
    if household:
        ids.add(household.owner_user_id)
    return list(ids)


async def effective_data_user_ids(session: AsyncSession, user: User) -> list[int]:
    return await get_household_member_user_ids(session, user)
