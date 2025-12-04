# app/api/api_v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.api.api_v1.deps import get_db_safe
from app.crud.crud_user import get_user_by_email, create_user
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db_safe)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = create_user(db, user_in)
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_safe)
):
    # form_data.username ES EL EMAIL
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
