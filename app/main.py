from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.cache import cache_manager
from app.core.middleware import logging_middleware
from app.api.v1.workouts import router as workout_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache_manager._redis_url = settings.REDIS_URL
    cache_manager._default_ttl = settings.CACHE_TTL_DEFAULT
    
    await cache_manager.connect()

    try:
        yield
    finally:
        await cache_manager.disconnect()


app = FastAPI(lifespan=lifespan, title="FitMetrics API")

app.middleware("http")(logging_middleware)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(workout_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")


@app.get('/health')
def get_health():
    return {"status": "ok"}
