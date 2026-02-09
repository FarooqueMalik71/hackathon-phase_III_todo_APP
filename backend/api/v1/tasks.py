from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from models.task import Task, TaskCreate, TaskRead, TaskUpdate, PriorityEnum
from api.deps import get_current_user
from db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from services import task_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    current_user: dict = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_async_session)
):
    """Retrieve tasks for the authenticated user with optional filtering"""
    user_id = current_user["user_id"]
    return await task_service.list_tasks(db, user_id, completed=completed, skip=offset, limit=limit)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new task for the authenticated user"""
    user_id = current_user["user_id"]
    return await task_service.create_task(db, user_id, task_create)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get a specific task by ID for the authenticated user"""
    user_id = current_user["user_id"]
    return await task_service.get_task(db, user_id, task_id)


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a specific task by ID for the authenticated user"""
    user_id = current_user["user_id"]
    return await task_service.update_task(db, user_id, task_id, task_update)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a specific task by ID for the authenticated user"""
    user_id = current_user["user_id"]
    await task_service.delete_task(db, user_id, task_id)


@router.patch("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task_completion(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Toggle the completion status of a specific task for the authenticated user"""
    user_id = current_user["user_id"]
    return await task_service.toggle_task(db, user_id, task_id)
