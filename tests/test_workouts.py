# tests/test_workouts.py
import pytest
from httpx import AsyncClient
from uuid import UUID

from app.db.models.users import Users


class TestWorkoutsCreate:
    """Тесты создания тренировок"""

    @pytest.mark.asyncio
    async def test_create_workout_success(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Успешное создание тренировки"""
        client, user = authenticated_client

        payload = {
            "exercise_name": "Bench Press",
            "muscle_group": "Chest",
            "sets": 3,
            "reps": 10,
            "weight": 80.0,
        }

        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == str(user.id)
        assert data["sets"] == 3
        assert data["reps"] == 10
        assert data["weight"] == 80.0
        assert data["total_volume"] == 2400.0
        assert data["exercise"]["name"] == "Bench Press"
        assert data["exercise"]["muscle_group"] == "Chest"

    @pytest.mark.asyncio
    async def test_create_workout_unauthenticated(self, client: AsyncClient):
        """Неавторизованный запрос возвращает 401"""
        payload = {
            "exercise_name": "Squat",
            "muscle_group": "Legs",
            "sets": 5,
            "reps": 5,
            "weight": 100.0,
        }

        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "field_to_remove",
        ["exercise_name", "sets", "reps", "weight"],
    )
    async def test_create_workout_missing_field(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        field_to_remove: str,
    ):
        """Отсутствие обязательного поля возвращает 422"""
        client, _ = authenticated_client

        payload = {
            "exercise_name": "Deadlift",
            "muscle_group": "Back",
            "sets": 5,
            "reps": 5,
            "weight": 120.0,
        }
        del payload[field_to_remove]

        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "field,invalid_value",
        [
            ("sets", 0),
            ("sets", -1),
            ("sets", 51),
            ("reps", 0),
            ("reps", -10),
            ("reps", 201),
            ("weight", -50.0),
            ("exercise_name", ""),
            ("muscle_group", ""),
        ],
    )
    async def test_create_workout_invalid_values(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        field: str,
        invalid_value,
    ):
        """Невалидные значения возвращают 422"""
        client, _ = authenticated_client

        payload = {
            "exercise_name": "Squat",
            "muscle_group": "Legs",
            "sets": 4,
            "reps": 8,
            "weight": 100.0,
        }
        payload[field] = invalid_value

        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workout_default_muscle_group(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """muscle_group имеет дефолт 'general'"""
        client, _ = authenticated_client

        payload = {
            "exercise_name": "Push-ups",
            "sets": 3,
            "reps": 15,
            "weight": 0.0,
        }

        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["exercise"]["muscle_group"] == "general"

    @pytest.mark.asyncio
    async def test_create_multiple_workouts_same_exercise(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Несколько тренировок с одним упражнением используют один Exercise"""
        client, _ = authenticated_client

        payload1 = {
            "exercise_name": "Bench Press",
            "muscle_group": "Chest",
            "sets": 3,
            "reps": 10,
            "weight": 80.0,
        }

        payload2 = {
            "exercise_name": "Bench Press",
            "muscle_group": "Chest",
            "sets": 4,
            "reps": 8,
            "weight": 90.0,
        }

        response1 = await client.post("/api/v1/workouts/", json=payload1)
        assert response1.status_code == 200

        response2 = await client.post("/api/v1/workouts/", json=payload2)
        assert response2.status_code == 200

        ex1_id = response1.json()["exercise"]["id"]
        ex2_id = response2.json()["exercise"]["id"]
        assert ex1_id == ex2_id


class TestWorkoutsList:
    """Тесты получения списка тренировок"""

    @pytest.mark.asyncio
    async def test_list_workouts_success(
        self,
        auth_client_with_workouts: tuple[AsyncClient, Users],
    ):
        """Получение списка своих тренировок"""
        client, user = auth_client_with_workouts

        response = await client.get("/api/v1/workouts/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3

        for workout in data:
            assert workout["user_id"] == str(user.id)
            assert "exercise" in workout
            assert "name" in workout["exercise"]
            assert workout["total_volume"] > 0

    @pytest.mark.asyncio
    async def test_list_workouts_empty(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Пользователь без тренировок получает пустой список"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/workouts/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_workouts_unauthenticated(self, client: AsyncClient):
        """Неавторизованный запрос возвращает 401"""
        response = await client.get("/api/v1/workouts/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_workouts_pagination(
        self,
        auth_client_with_workouts: tuple[AsyncClient, Users],
    ):
        """Пагинация работает корректно"""
        client, _ = auth_client_with_workouts

        response = await client.get("/api/v1/workouts/?limit=2&offset=0")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        response = await client.get("/api/v1/workouts/?limit=2&offset=2")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 1

        page1_ids = {w["id"] for w in page1}
        page2_ids = {w["id"] for w in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestWorkoutsIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    async def test_create_and_list_workflow(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Полный цикл: создать → получить в списке"""
        client, user = authenticated_client

        response = await client.get("/api/v1/workouts/")
        assert response.status_code == 200
        assert len(response.json()) == 0

        payload = {
            "exercise_name": "Squat",
            "muscle_group": "Legs",
            "sets": 5,
            "reps": 5,
            "weight": 100.0,
        }

        create_response = await client.post("/api/v1/workouts/", json=payload)
        assert create_response.status_code == 200
        created = create_response.json()

        list_response = await client.get("/api/v1/workouts/")
        assert list_response.status_code == 200

        workouts = list_response.json()
        assert len(workouts) == 1
        assert workouts[0]["id"] == created["id"]

    @pytest.mark.asyncio
    async def test_users_isolation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        user_with_workouts: Users,
    ):
        """Разные пользователи не видят чужие тренировки"""
        client, user1 = authenticated_client

        payload = {
            "exercise_name": "Dips",
            "muscle_group": "Chest",
            "sets": 3,
            "reps": 10,
            "weight": 20.0,
        }
        response = await client.post("/api/v1/workouts/", json=payload)
        assert response.status_code == 200

        response = await client.get("/api/v1/workouts/")
        assert response.status_code == 200
        user1_workouts = response.json()
        assert len(user1_workouts) == 1

        for workout in user1_workouts:
            assert workout["user_id"] == str(user1.id)
