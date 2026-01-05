# app/services/workout_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workout_repo import WorkoutRepository
from app.db.models.workout import Workout, Exercise
from app.schemas.workout import WorkoutCreate


class WorkoutService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = WorkoutRepository(session)

    async def create_workout(self, payload: WorkoutCreate) -> Workout:
        async with self._session.begin():
            return await self._repo.create_workout(payload)

    async def list_workouts(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[Workout]:
        list_workouts = await self._repo.list_workouts(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return list_workouts
    
    #TODO async def metrics(
    #     self,
        
            


    # )
