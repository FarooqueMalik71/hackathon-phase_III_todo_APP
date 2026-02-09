"""
Task Integration Service for AI chatbot
Routes all task operations through the shared task_service (same code path as REST API).
"""
import sys
import os
from typing import Dict, Any, Optional

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from models.task import TaskCreate, TaskUpdate
from services import task_service
from sqlalchemy.ext.asyncio import AsyncSession


class TaskIntegrationService:
    """Async service that delegates to the shared task_service functions."""

    async def add_task(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new task via the shared task service."""
        try:
            from datetime import datetime

            task_data = TaskCreate(
                title=title,
                description=description or "",
                priority=priority or "medium",
            )
            if due_date:
                try:
                    task_data.due_date = datetime.fromisoformat(
                        due_date.replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            task = await task_service.create_task(session, user_id, task_data)
            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "message": f"Task '{title}' added successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add task: {str(e)}",
            }

    async def complete_task(
        self, session: AsyncSession, user_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Mark a task as completed via the shared task service."""
        try:
            task = await task_service.get_task(session, user_id, task_id)
            if task.completed:
                return {
                    "success": True,
                    "task_id": str(task.id),
                    "message": f"Task '{task.title}' is already completed",
                }
            task = await task_service.toggle_task(session, user_id, task_id)
            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' marked as completed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete task: {str(e)}",
            }

    async def list_tasks(
        self,
        session: AsyncSession,
        user_id: str,
        completed: Optional[bool] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List tasks via the shared task service."""
        try:
            tasks = await task_service.list_tasks(
                session, user_id, completed=completed, limit=limit
            )
            task_list = [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "priority": t.priority if isinstance(t.priority, str) else t.priority.value,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                }
                for t in tasks
            ]
            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "message": f"Found {len(task_list)} tasks",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list tasks: {str(e)}",
            }

    async def update_task(
        self,
        session: AsyncSession,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a task via the shared task service."""
        try:
            from datetime import datetime

            update_fields = {}
            if title is not None:
                update_fields["title"] = title
            if description is not None:
                update_fields["description"] = description
            if priority is not None:
                update_fields["priority"] = priority
            if due_date is not None:
                try:
                    update_fields["due_date"] = datetime.fromisoformat(
                        due_date.replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            task_update = TaskUpdate(**update_fields)
            task = await task_service.update_task(
                session, user_id, task_id, task_update
            )
            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' updated successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update task: {str(e)}",
            }

    async def delete_task(
        self, session: AsyncSession, user_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Delete a task via the shared task service."""
        try:
            # Get task title before deletion for confirmation message
            task = await task_service.get_task(session, user_id, task_id)
            task_title = task.title
            await task_service.delete_task(session, user_id, task_id)
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{task_title}' deleted successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete task: {str(e)}",
            }
