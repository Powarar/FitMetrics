# app/services/metrics.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cached
from app.repositories.metrics_repo import MetricsRepository, MetricsSummaryRow, WorkoutCountRow


class MetricsService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = MetricsRepository(session)

    @cached(key_pattern="metrics:summary:days:{days}", ttl=600)
    async def get_summary(self, days: int) -> MetricsSummaryRow:
        return await self._repo.get_summary(days=days)
    
    @cached(key_pattern="metrics:timeline:user:{user_id}:days:{days}", ttl=900)
    async def get_workout_timeline(
        self,
        user_id: int,
        days: int,
    ) -> list[WorkoutCountRow]:
        rows = await self._repo.get_workout_timeline(user_id=user_id, days=days)
        return list(rows)