from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User, UserProject, UserProjectMessage


async def create_project(
    session: AsyncSession,
    user: User,
    *,
    title: str,
    description: str = "",
    project_type: str = "general",
) -> UserProject:
    project = UserProject(
        user_id=user.id,
        title=title.strip()[:255],
        description=description.strip()[:4000],
        project_type=project_type[:32],
    )
    session.add(project)
    await session.flush()
    user.active_project_id = project.id
    await session.commit()
    await session.refresh(project)
    return project


async def list_projects(session: AsyncSession, user_id: int, *, limit: int = 20) -> list[UserProject]:
    rows = (
        await session.execute(
            select(UserProject)
            .where(UserProject.user_id == user_id, UserProject.active.is_(True))
            .order_by(UserProject.updated_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def get_project(session: AsyncSession, user_id: int, project_id: int) -> UserProject | None:
    return (
        await session.execute(
            select(UserProject).where(UserProject.id == project_id, UserProject.user_id == user_id, UserProject.active.is_(True))
        )
    ).scalar_one_or_none()


async def get_active_project(session: AsyncSession, user: User) -> UserProject | None:
    if not user.active_project_id:
        return None
    return await get_project(session, user.id, user.active_project_id)


async def set_active_project(session: AsyncSession, user: User, project_id: int) -> bool:
    project = await get_project(session, user.id, project_id)
    if not project:
        return False
    user.active_project_id = project.id
    await session.commit()
    return True


async def append_project_message(
    session: AsyncSession,
    project_id: int,
    *,
    role: str,
    content: str,
) -> None:
    msg = UserProjectMessage(project_id=project_id, role=role[:16], content=content[:8000])
    session.add(msg)
    await session.execute(
        update(UserProject).where(UserProject.id == project_id).values(updated_at=datetime.utcnow())
    )
    await session.commit()


async def get_project_context(session: AsyncSession, project_id: int, *, limit: int = 12) -> str:
    project = (await session.execute(select(UserProject).where(UserProject.id == project_id))).scalar_one_or_none()
    if not project:
        return ""
    rows = (
        await session.execute(
            select(UserProjectMessage)
            .where(UserProjectMessage.project_id == project_id)
            .order_by(UserProjectMessage.id.desc())
            .limit(limit)
        )
    ).scalars().all()
    parts = [f"Project: {project.title}", project.description[:500], project.summary[:800]]
    for row in reversed(list(rows)):
        parts.append(f"{row.role}: {row.content[:400]}")
    return "\n".join(p for p in parts if p)


async def update_project_summary(session: AsyncSession, project_id: int, summary: str) -> None:
    await session.execute(
        update(UserProject).where(UserProject.id == project_id).values(summary=summary[:4000], updated_at=datetime.utcnow())
    )
    await session.commit()
