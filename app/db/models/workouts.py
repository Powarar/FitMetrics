from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    muscle_group: Mapped[str]

    workouts: Mapped[list["Workout"]] = relationship(back_populates="exercise")


class Workout(Base):
    __tablename__ = "workouts"
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    performed_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    sets: Mapped[int]
    reps: Mapped[int]
    weight: Mapped[float]
    total_volume: Mapped[float]

    exercise_id: Mapped[UUID] = mapped_column(ForeignKey("exercises.id"))
    
    exercise: Mapped["Exercise"] = relationship(back_populates="workouts")
    user: Mapped["Users"] = relationship(back_populates="workouts")
