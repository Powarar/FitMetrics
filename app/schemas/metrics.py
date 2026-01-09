from pydantic import BaseModel, Field
from datetime import date as Date

class MetricsSummaryResponse(BaseModel):
    total_volume: float = Field(..., description="Суммарный тренировочный объём")
    avg_volume: float = Field(..., description="Средний объём на тренировку")
    workouts_count: int = Field(..., description="Количество тренировок")

class WorkoutCountPoint(BaseModel):
    date: Date = Field(...)
    workouts_count: int = Field(...)