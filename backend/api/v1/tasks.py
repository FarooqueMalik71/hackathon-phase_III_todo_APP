from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from models.task import Task, TaskCreate, TaskRead, TaskUpdate, PriorityEnum
from api.deps import get_current_user
from db.session import get_async_session
from utils.auth import validate_user_access_to_task, filter_tasks_by_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import uuid


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    current_user: dict = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve tasks for the authenticated user with optional filtering
    """
    user_id = current_user["user_id"]

    # Build query with user filtering
    query = select(Task).where(Task.user_id == user_id)

    # Apply completion status filter if specified
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Apply ordering and pagination
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new task for the authenticated user
    """
    user_id = current_user["user_id"]

    # Ensure the task is created for the authenticated user
    task_data = task_create.dict()
    task_data["user_id"] = user_id

    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific task by ID for the authenticated user
    """
    user_id = current_user["user_id"]

    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    query = select(Task).where(Task.id == uuid_obj, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access forbidden"
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update a specific task by ID for the authenticated user
    """
    user_id = current_user["user_id"]

    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    query = select(Task).where(Task.id == uuid_obj, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access forbidden"
        )

    # Update task fields with provided values
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete a specific task by ID for the authenticated user
    """
    user_id = current_user["user_id"]

    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    query = select(Task).where(Task.id == uuid_obj, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access forbidden"
        )

    await db.delete(task)
    await db.commit()

    # Return 204 No Content as required by the specification


@router.patch("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task_completion(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Toggle the completion status of a specific task for the authenticated user
    """
    user_id = current_user["user_id"]

    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    query = select(Task).where(Task.id == uuid_obj, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access forbidden"
        )

    # Toggle the completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task