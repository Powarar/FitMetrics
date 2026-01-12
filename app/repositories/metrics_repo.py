from __future__ import annotations
from uuid import UUID  # ← Добавьте импорт

from datetime import datetime, timedelta
from typing import TypedDict, Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workouts import Workout
from app.repositories.workout_repo import WorkoutMetrics


class MetricsSummaryRow(TypedDict):
    total_volume: float
    avg_volume: float
    workouts_count: int


class WorkoutCountRow(TypedDict):
    date: datetime
    workouts_count: int


class MetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(
        self, 
        user_id: UUID,  # ← Добавлен + UUID
        days: int
    ) -> MetricsSummaryRow:
        """Сводка метрик для конкретного пользователя."""
        date_from = datetime.now() - timedelta(days=days)

        stmt: Select = (
            select(
                func.coalesce(func.sum(Workout.total_volume), 0).label("total_volume"),
                func.coalesce(func.avg(Workout.total_volume), 0).label("avg_volume"),
                func.count(Workout.id).label("workouts_count"),
            )
            .where(
                Workout.user_id == user_id,  # ← Критично! Только свои данные
                Workout.performed_at >= date_from
            )
        )

        result = await self._session.execute(stmt)
        row = result.one()

        return MetricsSummaryRow(
            total_volume=row.total_volume,
            avg_volume=row.avg_volume,
            workouts_count=row.workouts_count,
        )

    async def get_workout_timeline(
        self,
        user_id: UUID,  # int → UUID
        days: int,
    ) -> Sequence[WorkoutCountRow]:
        date_from = datetime.now() - timedelta(days=days)

        stmt: Select = (
            select(
                func.date(Workout.performed_at).label("date"),
                func.count(Workout.id).label("workouts_count"),
            )
            .where(
                Workout.user_id == user_id,  # Уже было, но тип исправлен
                Workout.performed_at >= date_from,
            )
            .group_by(func.date(Workout.performed_at))
            .order_by(func.date(Workout.performed_at))
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        return [
            WorkoutCountRow(
                date=row["date"],
                workouts_count=row["workouts_count"],
            )
            for row in rows
        ]

