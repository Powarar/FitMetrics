# app/schemas/users.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, SecretStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: SecretStr = Field(min_length=8)


class UserOut(UserBase):
    id: UUID
    is_active: bool

    class Config:
        from_attributes = True