"""Слой репозитория для доступа к данным тренировок и упражнений."""

from collections.abc import Sequence
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.workout import Exercise, Workout
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
    
    async def create_workout(self, payload: WorkoutCreate) -> Workout:
        """Создать новую тренировку со связанным упражнением."""
        exercise = await self.get_or_create_exercise(
            name=payload.exercise_name,
            muscle_group=payload.muscle_group,
        )
        
        workout = Workout(
            **payload.model_dump(exclude={"exercise_name", "muscle_group"}),
            exercise=exercise,
            total_volume=payload.sets * payload.reps * payload.weight,
        )
        
        self._session.add(workout)
        return workout
    
    async def list_workouts(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Workout]:
        """Получить список тренировок пользователя с пагинацией."""
        stmt = (
            select(Workout)
            .options(joinedload(Workout.exercise))
            .where(Workout.user_id == user_id)
            .order_by(Workout.performed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def metrics(self, user_id: int) -> WorkoutMetrics:
        """Рассчитать агрегированные метрики тренировок пользователя."""
        stmt = (
            select(
                func.coalesce(func.sum(Workout.total_volume), 0).label("total"),
                func.coalesce(func.avg(Workout.total_volume), 0).label("avg"),
                func.count(Workout.id).label("count"),
            )
            .where(Workout.user_id == user_id)
        )
        
        result = await self._session.execute(stmt)
        row = result.one()
        
        return WorkoutMetrics(
            total_volume=float(row.total),
            avg_volume=float(row.avg),
            count=int(row.count), # type: ignore
        )
