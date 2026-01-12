from datetime import datetime
from uuid import uuid4
from redis.asyncio import Redis
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.users import Users
from app.schemas.token import Token
from app.schemas.users import UserCreate
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


class UserService:
    def __init__(self, session: AsyncSession, redis_client: Redis | None = None):
        self.session = session
        self.redis = redis_client

    async def register(self, user_in: UserCreate) -> Users:
        existing = await self.session.execute(
            select(Users).where(Users.email == user_in.email)
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        user = Users(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password.get_secret_value()),
            is_active=True,
        )
        
        self.session.add(user)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(user)
        return user



    async def authenticate(self, email: str, password: str) -> Token:
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
        access_token = create_access_token({"sub": str(user.id)})
        return Token(access_token=access_token)


    async def get_by_id(self, user_id):
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )
        user: Users | None = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def logout(self, token: str) -> None:
        payload = decode_access_token(token)

        jti = payload["jti"]
        exp = payload["exp"]

        if not jti or not exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        now = datetime.now().timestamp()
        ttl = int(exp - now)

        if ttl > 0 and self.redis:
            await self.redis.setex(
                f"blacklist:{jti}",
                ttl,
                "revoked"
            )
        return None