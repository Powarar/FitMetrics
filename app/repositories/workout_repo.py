
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.workout import Workout, Exercise

class WorkoutRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        res = await self.session.execute(select(Exercise).where(Exercise.name == name))
        return res.scalar_one_or_none()

    async def get_or_create_exercise(self, name: str, muscle_group: str) -> Exercise:
        ex = await self.get_exercise_by_name(name)
        if ex:
            return ex
        ex = Exercise(name=name, muscle_group=muscle_group)
        self.session.add(ex)
        return ex

    async def create_workout(
        self,
        user_id: int,
        exercise_name: str,
        muscle_group: str,
        sets: int,
        reps: int,
        weight: float,
    ) -> Workout:
        ex = await self.get_or_create_exercise(exercise_name, muscle_group)

        w = Workout(
            user_id=user_id,
            exercise=ex,
            sets=sets,
            reps=reps,
            weight=weight,
            total_volume=float(sets * reps * weight),
        )
        self.session.add(w)
        return w

    async def list_workouts(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Workout]:
        stmt = (
            select(Workout)
            .options(joinedload(Workout.exercise))
            .where(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def metrics(self, user_id: int) -> dict:
        stmt = select(
            func.coalesce(func.sum(Workout.total_volume), 0).label("total"),
            func.coalesce(func.avg(Workout.total_volume), 0).label("avg"),
            func.count(Workout.id).label("count"),
        ).where(Workout.user_id == user_id)

        res = await self.session.execute(stmt)
        row = res.one()
        return {"total_volume": float(row.total), "avg_volume": float(row.avg), "count": int(row.count)}
