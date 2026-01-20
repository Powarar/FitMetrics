from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.cache import cache_manager

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/redis")
async def redis_health():
    ok = await cache_manager.health_check()
    if ok:
        return {"status": "healthy", "service": "redis"}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"status": "unhealthy", "service": "redis"},
    )
