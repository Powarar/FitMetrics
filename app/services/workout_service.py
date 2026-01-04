# app/services/workout_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workout_repo import WorkoutRepository
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate


class WorkoutService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = WorkoutRepository(session)

    async def create_workout(self, payload: WorkoutCreate) -> Workout:
        async with self._session.begin():
            workout = await self._repo.create_workout(
                user_id=payload.user_id,
                exercise_name=payload.exercise_name,
                muscle_group=payload.muscle_group,
                sets=payload.sets,
                reps=payload.reps,
                weight=payload.weight,
            )
        return workout
