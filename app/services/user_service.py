# app/services/user_service.py
from uuid import uuid4
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.users import Users
from app.schemas.users import UserCreate
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, user_in: UserCreate) -> Users:
        existing = await self.session.execute(
            select(Users).where(Users.email == user_in.email)
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        user_data = {
            "id": uuid4(),
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password.get_secret_value()),
            "is_active": True,
        }

        async with self.session.begin():
            result = await self.session.execute(
                insert(Users).values(user_data).returning(Users)
            )
            user: Users = result.scalar_one()
        return user

    async def authenticate(self, email: str, password: str) -> Users:
        result = await self.session.execute(
            select(Users).where(Users.email == email)
        )
        user: Users | None = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        return user

    async def get_by_id(self, user_id):
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )
        user: Users | None = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
