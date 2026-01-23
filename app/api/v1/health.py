from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.session import get_session
from app.api.deps import get_redis

router = APIRouter(prefix="/health", tags=["system"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    checks = {
        "database": False,
        "redis": False,
    }

    # DB
    try:
        await db.execute(select(1))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Redis
    try:
        await redis.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False

    overall_ok = all(checks.values())
    status_code = (
        status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    payload = {
        "status": "ok" if overall_ok else "error",
        "checks": checks,
    }

    return JSONResponse(
        content=payload,
        status_code=status_code,
    )
