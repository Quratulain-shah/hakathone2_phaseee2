"""
Task routes for the Todo App backend API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

try:
    from dependencies import get_db_session, validate_user_id_match, get_user_id_from_token
    from models.task import Task
    from schemas.task import TaskCreate, TaskRead, TaskListResponse, TaskUpdate
    from models.user import User
except ImportError:
    from backend.dependencies import get_db_session, validate_user_id_match, get_user_id_from_token
    from backend.models.task import Task
    from backend.schemas.task import TaskCreate, TaskRead, TaskListResponse, TaskUpdate
    from backend.models.user import User


# Create API router for task endpoints
router = APIRouter()


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskListResponse:
    """
    Get a list of tasks for the specified user.

    Args:
        user_id: The ID of the user whose tasks to retrieve (validated against token)
        db_session: Database session for async operations

    Returns:
        TaskListResponse: Response containing a list of tasks for the user

    Raises:
        HTTPException: If there's an error retrieving the tasks
    """
    try:
        # Query tasks for the specified user
        # This ensures user isolation - only tasks belonging to the specified user are returned
        statement = select(Task).where(Task.user_id == user_id)
        result = await db_session.execute(statement)
        tasks = result.scalars().all()

        # Convert SQLModel Task objects to TaskRead Pydantic models
        # Use model_dump with mode='python' to get a plain dict
        task_reads = []
        for task in tasks:
            task_dict = {
                'title': task.title,
                'description': task.description,
                'completed': task.completed,
                'user_id': task.user_id,
                'id': task.id,
                'created_at': task.created_at,
                'updated_at': task.updated_at,
            }
            task_reads.append(TaskRead.model_validate(task_dict))

        # Return the tasks in the response model
        return TaskListResponse(tasks=task_reads)

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error retrieving tasks for user {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving tasks"
        )


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskRead:
    """
    Create a new task for the specified user.

    Args:
        task_create: Task data to create
        user_id: The ID of the user for whom to create the task (validated against token)
        db_session: Database session for async operations

    Returns:
        TaskRead: The created task with its ID and timestamps

    Raises:
        HTTPException: If there's an error creating the task or validation fails
    """
    try:
        # Create a new task instance with the validated user_id
        db_task = Task(
            **task_create.model_dump(),
            user_id=user_id
        )

        # Add the task to the database session
        db_session.add(db_task)

        # Commit the transaction to persist the task
        await db_session.commit()

        # Refresh the task to get the generated ID and timestamps
        await db_session.refresh(db_task)

        # Convert SQLModel Task to Pydantic TaskRead model
        task_dict = {
            'title': db_task.title,
            'description': db_task.description,
            'completed': db_task.completed,
            'user_id': db_task.user_id,
            'id': db_task.id,
            'created_at': db_task.created_at,
            'updated_at': db_task.updated_at,
        }
        return TaskRead.model_validate(task_dict)

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error creating task for user {user_id}: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the task"
        )


@router.get("/{user_id}/tasks/{id}", response_model=TaskRead)
async def get_task(
    id: int,
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskRead:
    """
    Get a specific task for the specified user.

    Args:
        id: The ID of the task to retrieve
        user_id: The ID of the user whose task to retrieve (validated against token)
        db_session: Database session for async operations

    Returns:
        TaskRead: The requested task with its details

    Raises:
        HTTPException: If the task doesn't exist or doesn't belong to the user
    """
    try:
        # Query for the specific task that belongs to the specified user
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
        result = await db_session.execute(statement)
        task = result.scalar_one_or_none()

        # If task doesn't exist or doesn't belong to the user, return 404
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Convert SQLModel Task to Pydantic TaskRead model
        task_dict = {
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'user_id': task.user_id,
            'id': task.id,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        }
        return TaskRead.model_validate(task_dict)

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error retrieving task {id} for user {user_id}: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the task"
        )


@router.put("/{user_id}/tasks/{id}", response_model=TaskRead)
async def update_task(
    id: int,
    task_update: TaskUpdate,
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskRead:
    """
    Update a specific task for the specified user.

    Args:
        id: The ID of the task to update
        task_update: Task data to update
        user_id: The ID of the user whose task to update (validated against token)
        db_session: Database session for async operations

    Returns:
        TaskRead: The updated task with its details

    Raises:
        HTTPException: If the task doesn't exist, doesn't belong to the user, or validation fails
    """
    try:
        # Query for the specific task that belongs to the specified user
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
        result = await db_session.execute(statement)
        task = result.scalar_one_or_none()

        # If task doesn't exist or doesn't belong to the user, return 404
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Prepare update data by filtering out None values to only update provided fields
        update_data = task_update.model_dump(exclude_unset=True)

        # Update task fields if they are provided in the request
        for field, value in update_data.items():
            setattr(task, field, value)

        # Commit the transaction to persist the changes
        await db_session.commit()

        # Refresh the task to get the updated timestamps
        await db_session.refresh(task)

        # Convert SQLModel Task to Pydantic TaskRead model
        task_dict = {
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'user_id': task.user_id,
            'id': task.id,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        }
        return TaskRead.model_validate(task_dict)

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error updating task {id} for user {user_id}: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the task"
        )


@router.patch("/{user_id}/tasks/{id}", response_model=TaskRead)
async def partial_update_task(
    id: int,
    task_update: TaskUpdate,
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskRead:
    """
    Partially update a specific task for the specified user.
    Only the fields provided in the request body will be updated.

    Args:
        id: The ID of the task to update
        task_update: Task data to partially update
        user_id: The ID of the user whose task to update (validated against token)
        db_session: Database session for async operations

    Returns:
        TaskRead: The updated task with its details

    Raises:
        HTTPException: If the task doesn't exist, doesn't belong to the user, or validation fails
    """
    try:
        # Query for the specific task that belongs to the specified user
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
        result = await db_session.execute(statement)
        task = result.scalar_one_or_none()

        # If task doesn't exist or doesn't belong to the user, return 404
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Prepare update data by filtering out None values to only update provided fields
        update_data = task_update.model_dump(exclude_unset=True)

        # Update task fields if they are provided in the request
        for field, value in update_data.items():
            setattr(task, field, value)

        # Commit the transaction to persist the changes
        await db_session.commit()

        # Refresh the task to get the updated timestamps
        await db_session.refresh(task)

        # Convert SQLModel Task to Pydantic TaskRead model
        task_dict = {
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'user_id': task.user_id,
            'id': task.id,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        }
        return TaskRead.model_validate(task_dict)

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error partially updating task {id} for user {user_id}: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while partially updating the task"
        )


@router.delete("/{user_id}/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: int,
    user_id: int = Depends(validate_user_id_match),
    db_session: AsyncSession = Depends(get_db_session)
) -> None:
    """
    Delete a specific task for the specified user.

    Args:
        id: The ID of the task to delete
        user_id: The ID of the user whose task to delete (validated against token)
        db_session: Database session for async operations

    Returns:
        None: Returns 204 No Content on successful deletion

    Raises:
        HTTPException: If the task doesn't exist or doesn't belong to the user
    """
    try:
        # Query for the specific task that belongs to the specified user
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
        result = await db_session.execute(statement)
        task = result.scalar_one_or_none()

        # If task doesn't exist or doesn't belong to the user, return 404
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Delete the task from the database
        await db_session.delete(task)

        # Commit the transaction to persist the deletion
        await db_session.commit()

        # Return 204 No Content as required for successful deletion
        return None

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error deleting task {id} for user {user_id}: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the task"
        )