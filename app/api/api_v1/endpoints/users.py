# app/api/api_v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.api_v1.deps import get_db_safe, get_current_active_user, get_current_superuser
from app.schemas.user import UserOut
from app.crud.crud_user import get_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db_safe), _=Depends(get_current_superuser)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return user
