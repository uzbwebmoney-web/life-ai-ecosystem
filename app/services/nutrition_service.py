from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.models.entities import NutritionGroceryItem, NutritionWaterDaily
from app.services.health_service import user_local_now

NUTRITION_MODULE = "nutrition"
ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very": 1.9,
}


def today_key(user=None, now: datetime | None = None) -> str:
    now = now or datetime.utcnow()
    if user is not None:
        now = user_local_now(user, now)
    return now.strftime("%Y-%m-%d")


def parse_int_amount(raw: str) -> int | None:
    try:
        val = int(float(raw.replace(" ", "").replace(",", ".").strip()))
        return val if val > 0 else None
    except ValueError:
        return None


def parse_float(raw: str) -> float | None:
    try:
        val = float(raw.replace(" ", "").replace(",", ".").strip())
        return val if val > 0 else None
    except ValueError:
        return None


def calculate_tdee(*, weight_kg: float, height_cm: float, age: int, sex: str, activity: str) -> int:
    if sex == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    factor = ACTIVITY_FACTORS.get(activity, 1.375)
    return int(round(bmr * factor))


NUTRITION_SUBMODULE_AI: dict[str, str] = {
    "diet": (
        "Подбирай сбалансированный рацион под цели пользователя: похудение, набор массы, "
        "здоровое питание. Учитывай предпочтения и ограничения."
    ),
    "calories": (
        "Помогай рассчитывать калорийность блюд и дневную норму. Объясняй формулы и давай "
        "ориентиры по белкам, жирам, углеводам."
    ),
    "recipes": (
        "Предлагай рецепты с ингредиентами, шагами и примерной калорийностью. "
        "Учитывай диетические ограничения."
    ),
}


def nutrition_submodule_description(sub_id: str, lang: str) -> str:
    key = f"nut_sub_{sub_id}"
    text = t(lang, key)
    return text if text != key else t(lang, "nut_ai_hint")


async def add_grocery_item(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    profile_id: int | None = None,
) -> NutritionGroceryItem:
    item = NutritionGroceryItem(user_id=user_id, profile_id=profile_id, title=title.strip()[:255])
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_grocery_items(session: AsyncSession, user_id: int) -> list[NutritionGroceryItem]:
    rows = (
        await session.execute(
            select(NutritionGroceryItem)
            .where(NutritionGroceryItem.user_id == user_id, NutritionGroceryItem.active.is_(True))
            .order_by(NutritionGroceryItem.done.asc(), NutritionGroceryItem.id.asc())
        )
    ).scalars().all()
    return list(rows)


async def toggle_grocery_item(session: AsyncSession, user_id: int, item_id: int) -> NutritionGroceryItem | None:
    item = (
        await session.execute(
            select(NutritionGroceryItem).where(
                NutritionGroceryItem.id == item_id,
                NutritionGroceryItem.user_id == user_id,
                NutritionGroceryItem.active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not item:
        return None
    item.done = not item.done
    await session.commit()
    await session.refresh(item)
    return item


def format_grocery_line(item: NutritionGroceryItem) -> str:
    mark = "✅" if item.done else "⬜"
    return f"{mark} {item.title}"


async def get_water_today(session: AsyncSession, user_id: int, user) -> NutritionWaterDaily:
    day = today_key(user)
    row = (
        await session.execute(
            select(NutritionWaterDaily).where(
                NutritionWaterDaily.user_id == user_id,
                NutritionWaterDaily.day_key == day,
            )
        )
    ).scalar_one_or_none()
    if row:
        return row
    row = NutritionWaterDaily(user_id=user_id, profile_id=user.active_profile_id, day_key=day)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_water(session: AsyncSession, user_id: int, user, ml: int) -> NutritionWaterDaily:
    row = await get_water_today(session, user_id, user)
    row.total_ml = int(row.total_ml or 0) + ml
    row.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(row)
    return row


def format_water_line(row: NutritionWaterDaily, lang: str = "ru") -> str:
    pct = min(100, int((row.total_ml / row.goal_ml) * 100)) if row.goal_ml else 0
    return t(lang, "nut_water_summary", total=row.total_ml, goal=row.goal_ml, pct=pct)
