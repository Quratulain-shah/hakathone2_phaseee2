"""
Utility functions for the Todo App backend API
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

try:
    from config import settings
except ImportError:
    from backend.config import settings


# Password hashing context - using pbkdf2 instead of bcrypt for Windows compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def update_timestamp():
    """
    Generate a new timestamp for updated_at fields
    """
    return datetime.utcnow()


def validate_user_ownership(user_id: int, task_user_id: int) -> bool:
    """
    Validate that a task belongs to the authenticated user
    """
    return user_id == task_user_id


def format_error_response(error_code: str, message: str, details: Optional[list] = None):
    """
    Format a structured error response
    """
    return {
        "code": error_code,
        "message": message,
        "details": details or []
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """
    Verify a JWT token and return the payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)  # Convert to int since JWT encodes as string
    except JWTError:
        return None
    except (ValueError, TypeError):
        return None