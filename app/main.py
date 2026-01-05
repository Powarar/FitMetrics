from fastapi import FastAPI
from app.core.middleware import logging_middleware
from app.api.v1.workouts import router as workout_router
app = FastAPI()

app.middleware("http")(logging_middleware)
app.include_router(workout_router)

@app.get('/health')
def get_health():
    return {"status" : "ok"}