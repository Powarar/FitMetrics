
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.exceptions import CreditionalsException
from app.db.session import get_session
from app.db.models.users import Users
from app.core.cache import cache_manager
from app.services.user_service import UserService
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_redis() -> Redis:
    return cache_manager.get_client()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis)
) -> Users:

    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        
        if user_id_str is None:
            raise CreditionalsException
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise CreditionalsException

    if jti:
            is_blacklisted = await redis.exists(f"blacklist:{jti}")
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )



    service = UserService(session=session)
    return await service.get_by_id(user_id)

