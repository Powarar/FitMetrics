"""Слой бизнес-логики для операций с тренировками."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workout import Workout
from app.repositories.workout_repo import WorkoutMetrics, WorkoutRepository
from app.schemas.workout import WorkoutCreate


class WorkoutService:
    """Сервис для бизнес-логики работы с тренировками."""
    
    __slots__ = ("_session", "_repo")
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = WorkoutRepository(session)
    
    async def create_workout(self, payload: WorkoutCreate) -> Workout:
        """Создать новую тренировку в рамках транзакции."""
        async with self._session.begin():
            return await self._repo.create_workout(payload)
    
    async def list_workouts(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> Sequence[Workout]:
        """Получить постраничный список тренировок пользователя."""
        return await self._repo.list_workouts(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
    
    async def get_metrics(self, user_id: int) -> WorkoutMetrics:
        """Получить агрегированные метрики тренировок пользователя."""
        return await self._repo.metrics(user_id=user_id)
