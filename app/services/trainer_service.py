from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.ai_service import ask_ai
from app.services.analytics_service import analyze_fitness_gaps


async def run_trainer_turn(
    session: AsyncSession,
    user: User,
    message: str,
    *,
    bot=None,
    lang: str = "ru",
) -> str:
    stats = await analyze_fitness_gaps(session, user, days=30)
    prompt = (
        f"Сообщение пользователя: {message}\n\n"
        f"Статистика тренировок:\n{stats}\n\n"
        "Режим AI-тренера:\n"
        "1. Короткая мотивация\n"
        "2. Конкретный план на сегодня/неделю\n"
        "3. Одно actionable задание\n"
        "Будь энергичным, но реалистичным."
    )
    return await ask_ai(
        user_message=prompt,
        module_hint="Fitness trainer — personalized workout coaching.",
        language=lang,
        session=session,
        user=user,
        bot=bot,
        max_completion_tokens=1800,
        module_id="fitness",
        submodule_id="workouts",
        usage_source="agent_trainer",
    )
