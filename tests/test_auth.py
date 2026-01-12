# tests/test_auth.py
import pytest
from httpx import AsyncClient

from app.db.models.users import Users


class TestAuth:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """ Успешная регистрация нового пользователя (без username)"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data


    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user: Users,
    ):
        """ Регистрация с существующим email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email, 
                "password": "password123",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: Users):
        """ Успешный логин по email + password"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user.email,  # OAuth2PasswordRequestForm.username
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user: Users,
    ):
        """ Неверный пароль"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """ Логин несуществующего пользователя"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "no_user@example.com",
                "password": "anypassword",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_authenticated(
        self,
        authenticated_client: tuple[AsyncClient, Users],
    ):
        """ Получение информации о текущем пользователе"""
        client, user = authenticated_client

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        # username в схеме нет → не проверяем

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """ /me без токена — 401"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_email",
        [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
        ],
    )
    async def test_register_invalid_email(
        self,
        client: AsyncClient,
        invalid_email: str,
    ):
        """ Регистрация с невалидным email (валидация Pydantic → 422)"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": invalid_email,
                "password": "password123",
            },
        )

        assert response.status_code == 422
