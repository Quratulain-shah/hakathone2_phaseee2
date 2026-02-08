"""
Dependency injection functions for the Todo App backend API
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

try:
    from database import async_engine
    from models.user import User
    from utils import verify_token
except ImportError:
    from backend.database import async_engine
    from backend.models.user import User
    from backend.utils import verify_token


# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency
    """
    async with AsyncSession(async_engine) as session:
        yield session


def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> int:
    """
    Extract and validate user ID from JWT token
    """
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


async def get_current_user(
    user_id: int = Depends(get_user_id_from_token),
    db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get current authenticated user from JWT token using the shared session
    """
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def validate_user_id_match(user_id: int, token_user_id: int = Depends(get_user_id_from_token)):
    """
    Validate that the user_id in the path matches the authenticated user
    """
    if user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user"
        )
    return user_id