"""Модуль аутентификации и авторизации."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import crud, models
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Создать JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )


def decode_token(token: str) -> Optional[dict]:
    """Декодировать JWT token."""
    try:
        return jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Получить текущего пользователя из JWT токена.
    
    Raises:
        HTTPException: 401 при неверных учётных данных
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=payload["sub"])
    if not user or not user.is_active:
        raise credentials_exception
    
    return user


def require_roles(*allowed_roles: str):
    """
    Декоратор для проверки ролей пользователя.
    
    Args:
        *allowed_roles: Разрешённые роли (user, moderator, admin)
    """
    def role_checker(
        current_user: models.User = Depends(get_current_user)
    ) -> models.User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker