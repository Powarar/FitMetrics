# tests/conftest.py
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import delete

from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.api.deps import get_redis, get_current_user
from app.db.models.users import Users
from app.core.security import get_password_hash

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5433/test_fitmetrics"


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
        await session.execute(delete(Users))
        await session.commit()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для тестирования API с подменённой БД и Redis"""

    async def override_get_db():
        yield db_session

    class MockRedis:
        async def setex(self, *args, **kwargs):
            return True

        async def delete(self, *args, **kwargs):
            return True

        async def get(self, *args, **kwargs):
            return None

    async def override_get_redis():
        return MockRedis()

    app.dependency_overrides[get_session] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> Users:
    """Создаём тестового пользователя БЕЗ username"""
    user = Users(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user: Users,
) -> tuple[AsyncClient, Users]:
    """Клиент с авторизованным пользователем"""

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    return client, test_user
