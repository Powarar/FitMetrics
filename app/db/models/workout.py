from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Exercise(Base, AsyncAttrs):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    muscle_group: Mapped[str]

    workouts: Mapped[List["Workout"]] = relationship(back_populates="exercise")


class Workout(Base, AsyncAttrs):
    __tablename__ = "workouts"
    
    user_id: Mapped[int] = mapped_column(index=True)
    date: Mapped[datetime] = mapped_column(server_default=func.now())

    sets: Mapped[int]
    reps: Mapped[int]
    weight: Mapped[float]
    total_volume: Mapped[float]

    exercise_id: Mapped[UUID] = mapped_column(ForeignKey("exercises.id"))
    exercise: Mapped["Exercise"] = relationship(back_populates="workouts")
