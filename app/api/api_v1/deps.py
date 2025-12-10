# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.core.security import verify_token
from app.crud.crud_user import get_user, get_user_by_id
from app.models.user import User

# IMPORTANTE: La URL debe coincidir con tu endpoint de login
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=True
)


def get_db_safe():
    """Dependencia segura para la base de datos"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_safe)
) -> User:
    """
    Obtiene el usuario actual a partir del token JWT.
    
    Args:
        token: Token JWT obtenido del header Authorization
        db: Sesión de base de datos
    
    Returns:
        Objeto User del usuario autenticado
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # Verificar el token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer el user_id del token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identificador de usuario",
        )
    
    # Convertir a int y obtener el usuario
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de ID de usuario inválido en el token",
        )
    
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica que el usuario actual esté activo.
    
    Args:
        current_user: Usuario obtenido de get_current_user
    
    Returns:
        Usuario si está activo
    
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verifica que el usuario actual sea superusuario.
    
    Args:
        current_user: Usuario obtenido de get_current_active_user
    
    Returns:
        Usuario si es superusuario
    
    Raises:
        HTTPException: Si el usuario no es superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador",
        )
    return current_user


# Dependencias opcionales (para endpoints que pueden ser públicos o privados)
async def optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db_safe)
) -> Optional[User]:
    """
    Dependencia opcional para obtener usuario actual.
    Si no hay token, retorna None.
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def optional_current_active_user(
    user: Optional[User] = Depends(optional_current_user)
) -> Optional[User]:
    """
    Dependencia opcional para obtener usuario activo actual.
    Si no hay usuario o no está activo, retorna None.
    """
    if user is None or not user.is_active:
        return None
    return user