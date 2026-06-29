from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.services.ai_service import ask_ai


async def run_teacher_turn(
    session: AsyncSession,
    user: User,
    topic: str,
    *,
    bot=None,
    lang: str = "ru",
) -> str:
    level = user.knowledge_level or "standard"
    prompt = (
        f"Тема: {topic}\n\n"
        "Режим AI-преподавателя:\n"
        "1. Кратко объясни тему простым языком\n"
        "2. Приведи 1 пример\n"
        "3. Задай один проверочный вопрос ученику\n"
        "4. Не переходи к новой теме, пока ученик не ответит\n"
        f"Уровень ученика: {level}"
    )
    return await ask_ai(
        user_message=prompt,
        module_hint="Teacher mode — Socratic method, one question at a time.",
        language=lang,
        session=session,
        user=user,
        bot=bot,
        max_completion_tokens=2000,
        module_id="education",
        submodule_id="topics",
        usage_source="agent_teacher",
    )


async def run_teacher_check(
    session: AsyncSession,
    user: User,
    topic: str,
    student_answer: str,
    *,
    bot=None,
    lang: str = "ru",
) -> str:
    prompt = (
        f"Тема: {topic}\nОтвет ученика: {student_answer}\n\n"
        "Оцени ответ: правильно/частично/неправильно. Объясни ошибки. "
        "Если понял — похвали и задай следующий вопрос. Если нет — объясни проще."
    )
    return await ask_ai(
        user_message=prompt,
        module_hint="Teacher mode — evaluate student answer.",
        language=lang,
        session=session,
        user=user,
        bot=bot,
        max_completion_tokens=1500,
        module_id="education",
        usage_source="agent_teacher",
    )
