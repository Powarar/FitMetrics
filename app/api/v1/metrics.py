from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.metrics import MetricsSummaryResponse, WorkoutCountPoint
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_session),
) -> MetricsSummaryResponse:
    service = MetricsService(db)
    summary = await service.get_summary(days=days)
    return MetricsSummaryResponse(**summary)


@router.get("/timeline", response_model=list[WorkoutCountPoint])
async def get_workout_timeline(
    user_id: int = Query(..., gt=0),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_session),
) -> list[WorkoutCountPoint]:
    service = MetricsService(db)
    rows = await service.get_workout_timeline(user_id=user_id, days=days)
    return [WorkoutCountPoint(**row) for row in rows]