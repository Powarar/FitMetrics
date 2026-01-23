import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
import random

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.users import Users
from app.db.models.workouts import Exercise, Workout
from app.core.security import get_password_hash


async def seed_data():
    async with AsyncSessionLocal() as session:
        email = "test@fitmetrics.com"
        password = "password123"

        user = Users(
            email=email, hashed_password=get_password_hash(password), is_active=True
        )
        session.add(user)
        await session.flush()

        exercises_data = [
            ("Bench Press", "Chest"),
            ("Squat", "Legs"),
            ("Deadlift", "Back"),
            ("Overhead Press", "Shoulders"),
            ("Barbell Row", "Back"),
        ]

        exercises = []
        for name, muscle_group in exercises_data:
            ex = Exercise(name=name, muscle_group=muscle_group)
            session.add(ex)
            exercises.append(ex)

        await session.flush()

        training_days = [
            "2025-12-22",
            "2025-12-24",
            "2025-12-25",
            "2025-12-27",
            "2025-12-28",
            "2025-12-30",
            "2026-01-02",
            "2026-01-03",
            "2026-01-05",
            "2026-01-06",
            "2026-01-07",
            "2026-01-10",
            "2026-01-11",
            "2026-01-13",
            "2026-01-14",
            "2026-01-15",
            "2026-01-17",
            "2026-01-18",
            "2026-01-20",
        ]

        for day_str in training_days:
            day = datetime.strptime(day_str, "%Y-%m-%d")

            selected_exercises = random.sample(exercises, k=random.randint(2, 3))

            for exercise in selected_exercises:

                num_sets = random.randint(3, 5)

                for set_num in range(num_sets):
                    reps = random.randint(6, 12)

                    if exercise.name == "Squat":
                        weight = random.uniform(100, 140)
                    elif exercise.name == "Deadlift":
                        weight = random.uniform(120, 160)
                    elif exercise.name == "Bench Press":
                        weight = random.uniform(70, 100)
                    elif exercise.name == "Overhead Press":
                        weight = random.uniform(40, 60)
                    else:
                        weight = random.uniform(50, 80)

                    total_volume = reps * weight

                    workout = Workout(
                        user_id=user.id,
                        exercise_id=exercise.id,
                        performed_at=day + timedelta(hours=random.randint(9, 20)),
                        sets=1,
                        reps=reps,
                        weight=round(weight, 1),
                        total_volume=round(total_volume, 1),
                    )
                    session.add(workout)

        await session.commit()
        print("Фейковые данные добавлены!")
        print(f"Email: {email}")
        print(f"Password: {password}")


if __name__ == "__main__":
    asyncio.run(seed_data())
