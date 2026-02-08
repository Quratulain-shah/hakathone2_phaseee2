"""
Task schemas for the Todo App backend API
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """
    Base schema for task with common fields
    """
    title: str = Field(..., min_length=1, max_length=200, description="Task title (1-200 characters)")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description (up to 1000 characters)")
    completed: bool = Field(default=False, description="Whether the task is completed")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title must be between 1 and 200 characters"
    )


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task (partial updates allowed)
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskRead(TaskBase):
    """
    Schema for reading a task with its ID and timestamps
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """
    Schema for the response when listing tasks
    """
    tasks: List[TaskRead]