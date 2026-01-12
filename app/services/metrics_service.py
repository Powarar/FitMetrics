# app/services/metrics.py
from __future__ import annotations
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cached
from app.repositories.metrics_repo import MetricsRepository, MetricsSummaryRow, WorkoutCountRow
from app.repositories.workout_repo import WorkoutMetrics


class MetricsService:
    """Сервис метрик для текущего пользователя."""

    __slots__ = ("_repo", "_user_id", "_session")

    def __init__(self, session: AsyncSession, user_id: UUID) -> None:
        self._session = session
        self._repo = MetricsRepository(session)
        self._user_id = user_id

    @cached(key_pattern="metrics:summary:user:{user_id}:days:{days}", ttl=600)
    async def get_summary(self, days: int) -> MetricsSummaryRow:
        """Сводка метрик только для текущего пользователя."""
        return await self._repo.get_summary(
            user_id=self._user_id,
            days=days
        )

    @cached(key_pattern="metrics:timeline:user:{user_id}:days:{days}", ttl=900)
    async def get_workout_timeline(self, days: int) -> list[WorkoutCountRow]:
        """Таймлайн тренировок только для текущего пользователя."""
        rows = await self._repo.get_workout_timeline(
            user_id=self._user_id,  # ← Только свои данные
            days=days
        )
        return list(rows)