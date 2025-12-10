# app/api/api_v1/endpoints/users.py (ejemplo)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.api_v1.deps import get_db_safe  # Solo esto
from app.schemas.user import UserCreate, UserOut
from app.crud.crud_user import get_user_by_email, get_users, create_user, get_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db_safe)):
    """Crear usuario (público)"""
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(400, "Email ya registrado")
    return create_user(db, user_in)

@router.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_safe)):
    """Listar usuarios (público)"""
    return get_users(db, skip=skip, limit=limit)