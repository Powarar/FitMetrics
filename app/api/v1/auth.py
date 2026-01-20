# app/api/v1/auth.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.db.session import get_session
from app.schemas.users import UserCreate, UserOut
from app.schemas.token import Token
from app.services.user_service import UserService
from app.core.security import create_access_token, decode_access_token
from app.db.models.users import Users

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_user_service(
    session: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis)
) -> UserService:
    return UserService(session=session, redis_client=redis_client)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserOut:
    user: Users = await service.register(user_in)

    return user # type: ignore


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserService = Depends(get_user_service),
) -> Token:

    return await service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[Users, Depends(get_current_user)],
    token: Annotated[str, Depends(oauth2_scheme)],
    service: UserService = Depends(get_user_service)
) -> None:
    await service.logout(token)
    return None




@router.get("/me", response_model=UserOut)
async def read_me(
    current_user: Annotated[Users, Depends(get_current_user)],
) -> UserOut:
    return current_user # type: ignore
