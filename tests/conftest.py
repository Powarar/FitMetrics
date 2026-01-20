# tests/conftest.py
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timedelta

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import delete

from app.core.config import test_settings
from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.api.deps import get_redis, get_current_user
from app.db.models.users import Users
from app.db.models.workouts import Workout, Exercise
from app.core.security import get_password_hash


TEST_DATABASE_URL = test_settings.TEST_DATABASE_URL

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


# ============================================================================
# DATABASE SETUP
# ============================================================================


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Создаёт таблицы перед всеми тестами, удаляет после"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создаёт изолированную сессию БД с транзакцией.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session = TestSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


# ============================================================================
# HTTP CLIENT
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент с подменой зависимостей"""

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


# ============================================================================
# USER FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> Users:
    """Создаёт тестового пользователя"""
    user = Users(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user: Users,
) -> AsyncGenerator[tuple[AsyncClient, Users], None]:
    """HTTP клиент с аутентифицированным пользователем"""

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client, test_user
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession) -> Users:
    """Создаёт второго тестового пользователя"""
    user = Users(
        email="another@example.com",
        hashed_password=get_password_hash("another123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# WORKOUT FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def user_with_workouts(db_session: AsyncSession) -> Users:
    """
    Пользователь с 3 тренировками:
    - Bench Press: 3x10x80 кг = 2400 (2 дня назад)
    - Squat: 4x8x100 кг = 3200 (1 день назад)
    - Deadlift: 5x5x120 кг = 3000 (сегодня)

    Total volume: 8600
    Avg volume: 2866.67
    """
    user = Users(
        email="workouts_user@example.com",
        hashed_password=get_password_hash("workouts123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Создаём упражнения
    bench = Exercise(name="Bench Press", muscle_group="Chest")
    squat = Exercise(name="Squat", muscle_group="Legs")
    deadlift = Exercise(name="Deadlift", muscle_group="Back")

    db_session.add_all([bench, squat, deadlift])
    await db_session.commit()
    await db_session.refresh(bench)
    await db_session.refresh(squat)
    await db_session.refresh(deadlift)

    # Создаём тренировки
    workouts = [
        Workout(
            user_id=user.id,
            exercise_id=bench.id,
            sets=3,
            reps=10,
            weight=80.0,
            total_volume=2400.0,
            performed_at=datetime.now() - timedelta(days=2),
        ),
        Workout(
            user_id=user.id,
            exercise_id=squat.id,
            sets=4,
            reps=8,
            weight=100.0,
            total_volume=3200.0,
            performed_at=datetime.now() - timedelta(days=1),
        ),
        Workout(
            user_id=user.id,
            exercise_id=deadlift.id,
            sets=5,
            reps=5,
            weight=120.0,
            total_volume=3000.0,
            performed_at=datetime.now(),
        ),
    ]

    db_session.add_all(workouts)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def user_with_old_workouts(db_session: AsyncSession) -> Users:
    """Пользователь с тренировками старше 7 дней"""
    user = Users(
        email="old_workouts_user@example.com",
        hashed_password=get_password_hash("old123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    bench = Exercise(name="Bench Press Old", muscle_group="Chest")
    db_session.add(bench)
    await db_session.commit()
    await db_session.refresh(bench)

    old_workout = Workout(
        user_id=user.id,
        exercise_id=bench.id,
        sets=3,
        reps=10,
        weight=80.0,
        total_volume=2400.0,
        performed_at=datetime.now() - timedelta(days=10),
    )

    db_session.add(old_workout)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def auth_client_with_workouts(
    client: AsyncClient,
    user_with_workouts: Users,
) -> AsyncGenerator[tuple[AsyncClient, Users], None]:
    """HTTP клиент с пользователем, у которого есть тренировки"""

    async def override_get_current_user():
        return user_with_workouts

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client, user_with_workouts
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def auth_client_with_old_workouts(
    client: AsyncClient,
    user_with_old_workouts: Users,
) -> AsyncGenerator[tuple[AsyncClient, Users], None]:
    """HTTP клиент с пользователем, у которого есть старые тренировки"""

    async def override_get_current_user():
        return user_with_old_workouts

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client, user_with_old_workouts
    app.dependency_overrides.pop(get_current_user, None)
