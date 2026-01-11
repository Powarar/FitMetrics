from pydantic import BaseModel


class Token(BaseModel):
    """Схема ответа с токеном доступа."""
    
    access_token: str
    token_type: str = "bearer"