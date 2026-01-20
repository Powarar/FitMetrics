"Кастомные исключения"

from fastapi import HTTPException, status


class CreditionalsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong cridentionals",
            headers={"WWW-Authenticate": "Bearer"},
        )
