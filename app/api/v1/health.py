from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.cache import cache_manager

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/redis")
async def redis_health():
    ok = await cache_manager.health_check()
    if ok:
        return {"status": "healthy", "service": "redis"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "unhealthy", "service": "redis"},
    )