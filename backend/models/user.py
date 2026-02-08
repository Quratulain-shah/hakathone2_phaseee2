"""
User model for the Todo App backend API with authentication
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """
    Base class for User model containing common fields
    """
    email: str = Field(unique=True, nullable=False)


class User(UserBase, table=True):
    """
    User model with authentication support
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)


class UserRead(UserBase):
    """
    Schema for reading a user (without password)
    """
    id: int
    created_at: datetime
    is_active: bool


class UserCreate(SQLModel):
    """
    Schema for creating a new user
    """
    email: str
    password: str


class UserLogin(SQLModel):
    """
    Schema for user login
    """
    email: str
    password: str


class Token(SQLModel):
    """
    Schema for JWT token response
    """
    access_token: str
    token_type: str


class TokenData(SQLModel):
    """
    Schema for token data
    """
    user_id: Optional[int] = None