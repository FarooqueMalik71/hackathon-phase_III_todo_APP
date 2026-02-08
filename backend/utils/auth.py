from typing import Dict, Any, Optional
from sqlmodel import select
from models.task import Task
from db.session import get_sync_session
from fastapi import Depends, HTTPException, status


def verify_resource_ownership(user_id: str, resource_user_id: str) -> bool:
    """
    Verify that the authenticated user owns the resource
    """
    return user_id == resource_user_id


def check_task_ownership(user_id: str, task: Task) -> bool:
    """
    Check if the authenticated user owns the specified task
    """
    return verify_resource_ownership(user_id, task.user_id)


def validate_user_access_to_task(current_user_id: str, task: Task) -> None:
    """
    Validate that the current user has access to the specified task
    Raises HTTPException if access is not authorized
    """
    if not check_task_ownership(current_user_id, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this resource is forbidden"
        )


def filter_tasks_by_user(tasks_query, user_id: str):
    """
    Helper function to filter tasks by user_id
    """
    return tasks_query.where(Task.user_id == user_id)