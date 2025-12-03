# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate, is_superuser: bool = False):
    hashed = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, full_name=user_in.full_name, hashed_password=hashed, is_superuser=is_superuser)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
