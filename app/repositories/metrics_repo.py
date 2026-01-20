from __future__ import annotations
from uuid import UUID

from datetime import datetime, timedelta
from typing import TypedDict, Sequence

from sqlalchemy import Select, func, select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workouts import Workout


class MetricsSummaryRow(TypedDict):
    total_volume: float
    avg_volume: float
    workouts_count: int


class MetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(self, user_id: UUID, days: int) -> MetricsSummaryRow:
        """Сводка метрик для конкретного пользователя."""
        date_from = datetime.now() - timedelta(days=days)

        stmt: Select = select(
            func.coalesce(func.sum(Workout.total_volume), 0).label("total_volume"),
            func.coalesce(func.avg(Workout.total_volume), 0).label("avg_volume"),
            func.count(Workout.id).label("workouts_count"),
        ).where(Workout.user_id == user_id, Workout.performed_at >= date_from)

        result = await self._session.execute(stmt)
        row = result.one()

        return MetricsSummaryRow(
            total_volume=row.total_volume,
            avg_volume=row.avg_volume,
            workouts_count=row.workouts_count,
        )

    async def get_workout_timeline(
        self,
        user_id: UUID,
        days: int,
    ):
        """Сводка метрик для таймлайна тренировок"""
        start_date = datetime.now() - timedelta(days=days)

        stmt = (
            select(
                cast(Workout.performed_at, Date).label("date"),
                func.count(Workout.id).label("total_sets"),
                func.count(func.distinct(Workout.exercise_id)).label("workouts_count"),
                func.sum(Workout.total_volume).label("total_volume"),
                func.avg(Workout.weight).label("avg_weight"),
            )
            .where(Workout.user_id == user_id)
            .where(Workout.performed_at >= start_date)
            .group_by(cast(Workout.performed_at, Date))
            .order_by(cast(Workout.performed_at, Date))
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        timeline = {}
        current = start_date.date()
        end = datetime.now().date()

        while current <= end:
            timeline[current] = {
                "date": current,
                "workouts_count": 0,
                "total_sets": 0,
                "total_volume": 0.0,
                "avg_weight": None,
            }
            current += timedelta(days=1)

        for row in rows:
            timeline[row.date] = {
                "date": row.date,
                "workouts_count": row.workouts_count,
                "total_sets": row.total_sets,
                "total_volume": float(row.total_volume or 0),
                "avg_weight": float(row.avg_weight) if row.avg_weight else None,
            }

        return list(timeline.values())
