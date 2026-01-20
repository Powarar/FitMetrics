"""Слой репозитория для доступа к данным тренировок и упражнений."""

from collections.abc import Sequence
from typing import TypedDict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.workouts import Exercise, Workout
from app.schemas.workout import WorkoutCreate


class WorkoutMetrics(TypedDict):
    """Типобезопасный словарь с метриками тренировок."""

    total_volume: float
    avg_volume: float
    count: int


class WorkoutRepository:
    """Репозиторий для операций с тренировками и упражнениями в БД."""

    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_exercise_by_name(self, name: str) -> Exercise | None:
        """Получить упражнение по названию или вернуть None."""
        stmt = select(Exercise).where(Exercise.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_exercise(
        self,
        name: str,
        muscle_group: str | None = None,
    ) -> Exercise:
        """Получить существующее упражнение или создать новое."""
        if exercise := await self.get_exercise_by_name(name):
            return exercise

        exercise = Exercise(name=name, muscle_group=muscle_group)
        self._session.add(exercise)
        return exercise

    async def create_workout(self, payload: WorkoutCreate, user_id: UUID) -> Workout:
        """Создать новую тренировку со связанным упражнением."""
        exercise = await self.get_or_create_exercise(
            name=payload.exercise_name,
            muscle_group=payload.muscle_group,
        )

        workout = Workout(
            user_id=user_id,
            sets=payload.sets,
            reps=payload.reps,
            weight=payload.weight,
            total_volume=payload.sets * payload.reps * payload.weight,
            exercise=exercise,
        )

        self._session.add(workout)
        await self._session.flush()
        return workout

    async def list_workouts(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Workout]:
        """Получить список тренировок пользователя с пагинацией."""
        stmt = (
            select(Workout)
            .where(Workout.user_id == user_id)
            .options(selectinload(Workout.exercise))
            .limit(limit)
            .offset(offset)
            .order_by(Workout.performed_at.desc())
        )

        result = await self._session.execute(stmt)
        return result.scalars().all()
