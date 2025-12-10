# app/api/api_v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any

from app.api.api_v1.deps import get_db_safe, get_current_active_user
from app.crud.crud_user import get_user_by_email, create_user, get_user_by_id, authenticate_user
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token, verify_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db_safe)):
    """
    Registrar un nuevo usuario
    """
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email ya registrado"
        )
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_safe)
) -> Dict[str, Any]:
    """
    Iniciar sesión y obtener token de acceso
    
    Nota: form_data.username ES EL EMAIL según OAuth2PasswordRequestForm
    """
    # Usar authenticate_user que combina verificación de email y password
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=str(user.id),  # user.id como string
        expires_delta=access_token_expires,
        additional_data={
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active
        }
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active
    }


@router.post("/token", response_model=Token)
def login_oauth2_compatible(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_safe)
) -> Dict[str, Any]:
    """
    Endpoint compatible con OAuth2 para obtener token
    
    Usa el mismo endpoint que /login pero con nombre estándar OAuth2
    """
    return login_for_access_token(form_data, db)


@router.get("/me", response_model=UserOut)
def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actualmente autenticado
    """
    return current_user


@router.post("/refresh")
def refresh_token(
    token: str,
    db: Session = Depends(get_db_safe)
):
    """
    Refrescar token de acceso (implementación básica)
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene user_id",
        )
    
    try:
        user = get_user_by_id(db, int(user_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID inválido en el token",
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear nuevo token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        additional_data={
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active
        }
    )

    return {
        "access_token": new_access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "is_superuser": user.is_superuser
    }


@router.post("/validate-token")
def validate_token(
    token: str,
    db: Session = Depends(get_db_safe)
):
    """
    Validar si un token es válido y obtener información del usuario
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene user_id",
        )
    
    try:
        user = get_user_by_id(db, int(user_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID inválido en el token",
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "valid": True,
        "user_id": user.id,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "exp": payload.get("exp"),
        "token_type": payload.get("type", "access")
    }


@router.post("/logout")
def logout():
    """
    Cerrar sesión (en el cliente)
    
    Nota: Para JWT stateless, la invalidación se hace en el cliente
    eliminando el token. Para invalidación en servidor necesitarías
    una lista negra de tokens.
    """
    return {"message": "Sesión cerrada exitosamente. Elimina el token en el cliente."}


# Endpoint adicional para verificar salud del auth
@router.get("/health")
def auth_health():
    """
    Verificar que el módulo de autenticación esté funcionando
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "token_expire_minutes": settings.access_token_expire_minutes
    }