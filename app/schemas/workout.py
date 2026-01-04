from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class WorkoutCreate(BaseModel):
    user_id: int = Field(ge=1)
    exercise_name: str = Field(min_length=1, max_length=100)
    muscle_group: str = Field(default="general", min_length=1, max_length=50)
    sets: int = Field(ge=1, le=50)
    reps: int = Field(ge=1, le=200)
    weight: float = Field(ge=0)


class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: int
    date: datetime
    total_volume: float
    exercise_name: str



class MetricsOut(BaseModel):
    total_volume: float = 0.0
    avg_volume: float = 0.0
    count: int = 0
