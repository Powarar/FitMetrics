# tests/test_metrics.py
import pytest
from httpx import AsyncClient

from app.db.models.users import Users


class TestMetricsSummary:
    """Тесты /metrics/summary"""

    @pytest.mark.asyncio
    async def test_summary_with_workouts(
        self,
        auth_client_with_workouts: tuple[AsyncClient, Users],
    ):
        """Summary возвращает корректные метрики для пользователя с тренировками"""
        client, _ = auth_client_with_workouts

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_volume" in data
        assert "avg_volume" in data
        assert "workouts_count" in data
        
        assert data["total_volume"] == 8600.0
        assert data["workouts_count"] == 3
        assert 2866.0 < data["avg_volume"] < 2867.0

    @pytest.mark.asyncio
    async def test_summary_empty(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Summary для пользователя без тренировок возвращает нули"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_volume"] == 0.0
        assert data["avg_volume"] == 0.0
        assert data["workouts_count"] == 0

    @pytest.mark.asyncio
    async def test_summary_unauthenticated(self, client: AsyncClient):
        """Неавторизованный запрос возвращает 401"""
        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_summary_filters_by_days(
        self,
        auth_client_with_old_workouts: tuple[AsyncClient, Users],
    ):
        """Summary фильтрует тренировки по параметру days"""
        client, _ = auth_client_with_old_workouts

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["workouts_count"] == 0

        response = await client.get("/api/v1/metrics/summary?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["workouts_count"] == 1
        assert data["total_volume"] == 2400.0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "days,expected_status",
        [
            (1, 200),
            (7, 200),
            (30, 200),
            (365, 200),
            (0, 422),
            (-1, 422),
            (366, 422),
        ],
    )
    async def test_summary_days_validation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        days: int,
        expected_status: int,
    ):
        """Валидация параметра days (ge=1, le=365)"""
        client, _ = authenticated_client

        response = await client.get(f"/api/v1/metrics/summary?days={days}")
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_summary_user_isolation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        user_with_workouts: Users,
    ):
        """Метрики показывают только свои тренировки"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert data["workouts_count"] == 0
        assert data["total_volume"] == 0.0


class TestMetricsTimeline:
    """Тесты /metrics/timeline"""

    @pytest.mark.asyncio
    async def test_timeline_with_workouts(
        self,
        auth_client_with_workouts: tuple[AsyncClient, Users],
    ):
        """Timeline возвращает количество тренировок по дням"""
        client, _ = auth_client_with_workouts

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        for point in data:
            assert "date" in point
            assert "workouts_count" in point
            assert point["workouts_count"] > 0

    @pytest.mark.asyncio
    async def test_timeline_empty(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Timeline для пользователя без тренировок возвращает пустой список"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_timeline_unauthenticated(self, client: AsyncClient):
        """Неавторизованный запрос возвращает 401"""
        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_timeline_ordered_by_date(
        self,
        auth_client_with_workouts: tuple[AsyncClient, Users],
    ):
        """Timeline упорядочен по дате (ASC)"""
        client, _ = auth_client_with_workouts

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        
        data = response.json()
        dates = [point["date"] for point in data]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_timeline_filters_by_days(
        self,
        auth_client_with_old_workouts: tuple[AsyncClient, Users],
    ):
        """Timeline фильтрует по параметру days"""
        client, _ = auth_client_with_old_workouts

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        assert len(response.json()) == 0

        response = await client.get("/api/v1/metrics/timeline?days=30")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "days,expected_status",
        [
            (1, 200),
            (30, 200),
            (365, 200),
            (0, 422),
            (-5, 422),
            (366, 422),
        ],
    )
    async def test_timeline_days_validation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        days: int,
        expected_status: int,
    ):
        """Валидация параметра days"""
        client, _ = authenticated_client

        response = await client.get(f"/api/v1/metrics/timeline?days={days}")
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_timeline_user_isolation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
        user_with_workouts: Users,
    ):
        """Timeline показывает только свои тренировки"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        assert response.json() == []


class TestMetricsIntegration:
    """Интеграционные тесты метрик"""

    @pytest.mark.asyncio
    async def test_metrics_update_after_workout_creation(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Метрики обновляются после создания тренировки"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        assert response.json()["workouts_count"] == 0

        payload = {
            "exercise_name": "Squat",
            "muscle_group": "Legs",
            "sets": 5,
            "reps": 5,
            "weight": 100.0,
        }
        
        create_response = await client.post("/api/v1/workouts/", json=payload)
        assert create_response.status_code == 200

        response = await client.get("/api/v1/metrics/summary?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["workouts_count"] == 1
        assert data["total_volume"] == 2500.0

    @pytest.mark.asyncio
    async def test_timeline_groups_same_day_workouts(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Timeline группирует тренировки за один день"""
        client, _ = authenticated_client

        payload1 = {
            "exercise_name": "Bench Press",
            "muscle_group": "Chest",
            "sets": 3,
            "reps": 10,
            "weight": 80.0,
        }
        
        payload2 = {
            "exercise_name": "Squat",
            "muscle_group": "Legs",
            "sets": 4,
            "reps": 8,
            "weight": 100.0,
        }

        await client.post("/api/v1/workouts/", json=payload1)
        await client.post("/api/v1/workouts/", json=payload2)

        response = await client.get("/api/v1/metrics/timeline?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["workouts_count"] == 2
