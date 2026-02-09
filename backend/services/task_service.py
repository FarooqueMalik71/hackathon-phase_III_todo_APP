"""
Shared Task Service — Single source of truth for task CRUD operations.
Used by both REST API endpoints (api/v1/tasks.py) and chatbot MCP tools.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.task import Task, TaskCreate, TaskUpdate
from datetime import datetime
import uuid


async def list_tasks(
    session: AsyncSession,
    user_id: str,
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Task]:
    """List tasks for a user with optional filtering."""
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_task(
    session: AsyncSession,
    user_id: str,
    task_data: TaskCreate,
) -> Task:
    """Create a new task for the user."""
    data = task_data.dict()
    data["user_id"] = user_id
    task = Task(**data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(
    session: AsyncSession,
    user_id: str,
    task_id: str,
) -> Task:
    """Get a single task by ID, verifying ownership."""
    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format",
        )
    query = select(Task).where(Task.id == uuid_obj, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access forbidden",
        )
    return task


async def update_task(
    session: AsyncSession,
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
) -> Task:
    """Update a task's fields."""
    task = await get_task(session, user_id, task_id)
    update_fields = task_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(
    session: AsyncSession,
    user_id: str,
    task_id: str,
) -> None:
    """Delete a task by ID."""
    task = await get_task(session, user_id, task_id)
    await session.delete(task)
    await session.commit()


async def toggle_task(
    session: AsyncSession,
    user_id: str,
    task_id: str,
) -> Task:
    """Toggle a task's completion status."""
    task = await get_task(session, user_id, task_id)
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task
