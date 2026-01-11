
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CreditionalsException
from app.db.session import get_session
from app.db.models.users import Users
from app.services.user_service import UserService
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> Users:

    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise CreditionalsException
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise CreditionalsException

    service = UserService(session=session)
    return await service.get_by_id(user_id)