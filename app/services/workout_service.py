"""Слой бизнес-логики для операций с тренировками."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workouts import Workout
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.workout import WorkoutCreate
from app.core.cache import cache_manager


class WorkoutService:
    """Сервис для бизнес-логики работы с тренировками."""
    
    __slots__ = ("_session", "_repo", "_user_id")
    
    def __init__(self, session: AsyncSession, user_id: UUID) -> None:
        self._session = session
        self._repo = WorkoutRepository(session)
        self._user_id = user_id  

    async def _invalidate_metrics_cache(self) -> None:
        """Инвалидация кэша только для текущего пользователя."""
        await cache_manager.delete_pattern(f"metrics:summary:user:{self._user_id}:*")

    async def create_workout(self, payload: WorkoutCreate) -> Workout:
        """Создать новую тренировку (user_id подставляется автоматически)."""
        workout = await self._repo.create_workout(payload, self._user_id)
        await self._invalidate_metrics_cache()
        return workout

    async def list_workouts(self, limit: int, offset: int) -> Sequence[Workout]:
        """Получить список тренировок текущего пользователя."""
        return await self._repo.list_workouts(
            user_id=self._user_id,
            limit=limit,
            offset=offset,
        )
