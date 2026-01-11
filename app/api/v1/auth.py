# app/api/v1/auth.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.users import UserCreate, UserOut
from app.schemas.token import Token
from app.services.user_service import UserService
from app.core.security import create_access_token, decode_access_token
from app.db.models.users import Users

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(session=session)


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
    # OAuth2PasswordRequestForm использует username, поэтому под email:
    user_orm: Users = await service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    access_token = create_access_token({"sub": str(user_orm.id)})
    return Token(access_token=access_token)

#TODO переписать в deps
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    service = UserService(session=session)
    return await service.get_by_id(user_id)


@router.get("/me", response_model=UserOut)
async def read_me(
    current_user: Annotated[Users, Depends(get_current_user)],
) -> UserOut:
    return current_user # type: ignore
