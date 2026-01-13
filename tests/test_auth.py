# tests/test_auth.py (новый файл)
import pytest
from httpx import AsyncClient

from app.db.models.users import Users


class TestAuth:
    """Тесты аутентификации"""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """Получение своего профиля"""
        client, user = authenticated_client

        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user.email
        assert data["id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Неавторизованный запрос возвращает 401"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
