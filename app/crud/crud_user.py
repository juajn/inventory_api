# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    """Obtener usuario por email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Obtener usuario por nombre de usuario"""
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    """Obtener usuario por ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtener lista de usuarios con paginación"""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: UserCreate, is_superuser: bool = False):
    """Crear nuevo usuario"""
    # Verificar si el email ya existe
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise ValueError("Email ya registrado")
    
    # Si el esquema tiene username, verificar si ya existe
    if hasattr(user_in, 'username') and user_in.username:
        existing_username = get_user_by_username(db, user_in.username)
        if existing_username:
            raise ValueError("Nombre de usuario ya existe")
    
    # Crear hash de la contraseña
    hashed_password = get_password_hash(user_in.password)
    
    # Preparar datos del usuario
    user_data = {
        "email": user_in.email,
        "hashed_password": hashed_password,
        "is_superuser": is_superuser,
        "is_active": True  # Por defecto, usuarios activos
    }
    
    # Agregar campos adicionales si existen en el esquema
    if hasattr(user_in, 'full_name'):
        user_data["full_name"] = user_in.full_name
    if hasattr(user_in, 'username'):
        user_data["username"] = user_in.username
    
    # Crear usuario
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Actualizar usuario"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Si se actualiza la contraseña, hashearla
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Actualizar campos
    for field, value in update_data.items():
        if hasattr(user, field) and field != "password":
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    """Eliminar usuario (soft delete)"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    # Soft delete: marcar como inactivo en lugar de eliminar
    user.is_active = False
    db.add(user)
    db.commit()
    return user

def authenticate_user(db: Session, email: str, password: str):
    """Autenticar usuario por email y contraseña"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def change_user_password(db: Session, user_id: int, old_password: str, new_password: str):
    """Cambiar contraseña de usuario"""
    user = get_user(db, user_id)
    if not user:
        return False, "Usuario no encontrado"
    
    if not verify_password(old_password, user.hashed_password):
        return False, "Contraseña actual incorrecta"
    
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    return True, "Contraseña cambiada exitosamente"

def activate_user(db: Session, user_id: int):
    """Activar usuario"""
    user = get_user(db, user_id)
    if not user:
        return None
    user.is_active = True
    db.add(user)
    db.commit()
    return user

def deactivate_user(db: Session, user_id: int):
    """Desactivar usuario"""
    user = get_user(db, user_id)
    if not user:
        return None
    user.is_active = False
    db.add(user)
    db.commit()
    return user

def promote_to_superuser(db: Session, user_id: int):
    """Promover usuario a superusuario"""
    user = get_user(db, user_id)
    if not user:
        return None
    user.is_superuser = True
    db.add(user)
    db.commit()
    return user

def demote_from_superuser(db: Session, user_id: int):
    """Quitar privilegios de superusuario"""
    user = get_user(db, user_id)
    if not user:
        return None
    user.is_superuser = False
    db.add(user)
    db.commit()
    return user

def get_user_by_id(db: Session, user_id: int):
    """Alias para get_user por compatibilidad con auth.py"""
    return get_user(db, user_id)

def count_users(db: Session):
    """Contar total de usuarios"""
    return db.query(User).count()