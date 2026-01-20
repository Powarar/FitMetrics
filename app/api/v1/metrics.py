from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.api.v1.auth import get_current_user
from app.schemas.metrics import MetricsSummaryResponse
from app.schemas.workout import MetricsOut
from app.db.models.users import Users 
from app.services.metrics_service import MetricsService


router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_metrics_service(
    session: AsyncSession = Depends(get_session),
    current_user: Users = Depends(get_current_user)
):
    return MetricsService(session, user_id=current_user.id)


@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    days: int = Query(7, ge=1, le=365),
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsSummaryResponse:
    summary = await service.get_summary(days=days)
    return MetricsSummaryResponse(**summary)


@router.get("/timeline")
async def get_workout_timeline(
    days: int = Query(30, ge=1, le=365),
    service: MetricsService = Depends(get_metrics_service),
) -> list:
    rows = await service.get_workout_timeline(days=days)
    return rows
