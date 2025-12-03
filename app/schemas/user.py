# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True
