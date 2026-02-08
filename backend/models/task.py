"""
Task model for the Todo App backend API
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """
    Base class for Task model containing common fields
    """
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: int = Field(index=True)


class Task(TaskBase, table=True):
    """
    Task model representing a user's todo item
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    # Note: completed is inherited from TaskBase


class TaskCreate(TaskBase):
    """
    Schema for creating a new task
    """
    pass


class TaskUpdate(SQLModel):
    """
    Schema for updating an existing task
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """
    Schema for reading a task with its ID and timestamps
    """
    id: int
    created_at: datetime
    updated_at: datetime