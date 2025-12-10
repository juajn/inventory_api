# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, 
                         description="Contraseña de al menos 6 caracteres")
    confirm_password: Optional[str] = Field(None, 
                                           description="Confirmación de contraseña")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserOut(UserInDBBase):
    """Esquema para respuesta pública del usuario"""
    pass

class UserAdminOut(UserInDBBase):
    """Esquema para administradores (incluye más información)"""
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserChangePassword(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las nuevas contraseñas no coinciden')
        return v
    
    @validator('new_password')
    def different_password(cls, v, values, **kwargs):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        return v

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

class UserRegister(UserCreate):
    """Alias para UserCreate para registro público"""
    pass

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

# Para respuestas específicas
class UserResponse(BaseModel):
    success: bool
    message: str
    data: Optional[UserOut] = None

class UsersListResponse(BaseModel):
    success: bool
    count: int
    users: list[UserOut]

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut