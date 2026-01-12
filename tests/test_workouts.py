# tests/test_workouts.py
import pytest
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models.users import Users
from app.db.models.workouts import Workout


@pytest.fixture
def workout_data() -> dict:
    """Базовые данные для создания тренировки"""
    return {
        "user_id": 0,  # перезапишем в тесте реальным id
        "workout_type": "Running",
        "duration": 30,
        "calories": 300,
        "distance": 5.0,
        "date": datetime.now().isoformat(),
    }


@pytest.fixture
async def test_user_with_workout(
    db_session: AsyncSession,
) -> Users:
    """Пользователь + одна тренировка в БД"""
    user = Users(
        email="metrics@example.com",
        hashed_password=get_password_hash("metrics123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    workout = Workout(
        user_id=user.id,
        workout_type="Cycling",
        duration=45,
        calories=400,
        distance=15.0,
        date=datetime.now(),
    )
    db_session.add(workout)
    await db_session.commit()

    return user


class TestWorkouts:
    @pytest.mark.asyncio
    async def test_create_workout_success(
        self,
        client: AsyncClient,
        test_user: Users,
        workout_data: dict,
    ):
        """ Создание тренировки"""
        workout_data["user_id"] = test_user.id

        response = await client.post(
            "/api/v1/workouts",
            json=workout_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["workout_type"] == workout_data["workout_type"]
        assert data["duration"] == workout_data["duration"]
        assert data["calories"] == workout_data["calories"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_workouts(
        self,
        client: AsyncClient,
        test_user_with_workout: Users,
    ):
        """ Список тренировок по user_id"""
        response = await client.get(
            f"/api/v1/workouts?user_id={test_user_with_workout.id}",
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == test_user_with_workout.id

    @pytest.mark.asyncio
    async def test_get_workout_metrics(
        self,
        client: AsyncClient,
        test_user_with_workout: Users,
    ):
        """ Метрики по тренировкам пользователя"""
        response = await client.get(
            f"/api/v1/workouts/metrics/{test_user_with_workout.id}",
        )

        assert response.status_code == 200
        data = response.json()
        
        assert "total_workouts" in data
        assert "total_calories" in data
        assert "total_duration" in data
        assert data["total_workouts"] >= 1

    @pytest.mark.asyncio
    async def test_list_workouts_invalid_user_id(self, client: AsyncClient):
        """ Невалидный user_id в query → 422"""
        response = await client.get("/api/v1/workouts?user_id=-1")

        assert response.status_code == 422
