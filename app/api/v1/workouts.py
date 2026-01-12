from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.users import Users
from app.db.session import get_session
from app.schemas.workout import WorkoutCreate, WorkoutOut, MetricsOut
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.post("/workouts", response_model=WorkoutOut)
async def create_workout(
    payload: WorkoutCreate,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = WorkoutService(session=session, user_id=current_user.id)
    return await service.create_workout(payload)

@router.get("/workouts", response_model=list[WorkoutOut])
async def list_workouts(
    limit: int = 10,
    offset: int = 0,
    current_user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = WorkoutService(session=session, user_id=current_user.id)
    return await service.list_workouts(limit, offset)



