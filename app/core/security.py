# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera hash de una contraseña usando bcrypt.
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str, 
    expires_delta: Optional[timedelta] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        subject: Identificador del usuario (normalmente user_id)
        expires_delta: Tiempo de expiración del token
        additional_data: Datos adicionales para incluir en el token
    
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "iat": datetime.utcnow(),  # Fecha de emisión
        "type": "access"
    }
    
    # Agregar datos adicionales si existen
    if additional_data:
        to_encode.update(additional_data)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de refresh.
    
    Args:
        subject: Identificador del usuario
        expires_delta: Tiempo de expiración (por defecto 7 días)
    
    Returns:
        Token JWT de refresh
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Payload decodificado o None si el token es inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except PyJWTError:
        return None


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica un token JWT (alias para verify_token).
    
    Deprecated: Usar verify_token en su lugar.
    """
    return verify_token(token)


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Obtiene la fecha de expiración de un token.
    
    Args:
        token: Token JWT
    
    Returns:
        datetime de expiración o None si el token es inválido
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """
    Verifica si un token ha expirado.
    
    Args:
        token: Token JWT
    
    Returns:
        True si el token ha expirado, False en caso contrario
    """
    payload = verify_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    now = datetime.utcnow().timestamp()
    return exp < now


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrae el ID de usuario del token.
    
    Args:
        token: Token JWT
    
    Returns:
        ID de usuario o None si no se puede extraer
    """
    payload = verify_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None


def generate_password_reset_token(email: str) -> str:
    """
    Genera un token para restablecer contraseña.
    
    Args:
        email: Email del usuario
    
    Returns:
        Token JWT para restablecer contraseña
    """
    expires_delta = timedelta(minutes=settings.reset_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "iat": datetime.utcnow(),
        "type": "reset_password"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verifica un token de restablecimiento de contraseña.
    
    Args:
        token: Token JWT de restablecimiento
    
    Returns:
        Email del usuario o None si el token es inválido
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "reset_password":
        return payload.get("sub")
    return None


def generate_email_verification_token(email: str) -> str:
    """
    Genera un token para verificación de email.
    
    Args:
        email: Email del usuario
    
    Returns:
        Token JWT para verificación de email
    """
    expires_delta = timedelta(days=settings.email_verify_token_expire_days)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "iat": datetime.utcnow(),
        "type": "verify_email"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_email_token(token: str) -> Optional[str]:
    """
    Verifica un token de verificación de email.
    
    Args:
        token: Token JWT de verificación
    
    Returns:
        Email del usuario o None si el token es inválido
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "verify_email":
        return payload.get("sub")
    return None