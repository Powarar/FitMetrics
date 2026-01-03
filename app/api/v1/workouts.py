from typing import List

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutMetrics
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])


def get_workout_service(session: AsyncSession = Depends(get_session)) -> WorkoutService:
    return WorkoutService(session)


@router.post(
    "",
    response_model=WorkoutResponse,
    status_code=201,
)
async def create_workout(
    payload: WorkoutCreate,
    service: WorkoutService = Depends(get_workout_service),
) -> WorkoutResponse:
    workout = await service.create_workout(payload)
    return workout


@router.get(
    "",
    response_model=List[WorkoutResponse],
)
async def list_workouts(
    user_id: int = Query(..., gt=0),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: WorkoutService = Depends(get_workout_service),
) -> List[WorkoutResponse]:
    workouts = await service.list_workouts(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return workouts


@router.get(
    "/metrics/{user_id}",
    response_model=WorkoutMetrics,
)
async def get_workout_metrics(
    user_id: int = Path(..., gt=0),
    service: WorkoutService = Depends(get_workout_service),
) -> WorkoutMetrics:
    metrics = await service.metrics(user_id=user_id)
    return metrics
