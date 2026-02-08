"""
Task Integration Service for AI chatbot
Integrates with existing Phase II task backend services
"""
import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from models.task import Task, TaskCreate, TaskUpdate, PriorityEnum
from db.session import create_sync_session
from sqlmodel import select
import uuid
from datetime import datetime


class TaskIntegrationService:
    """Service for integrating with existing task backend"""

    def __init__(self):
        self.session = create_sync_session()

    def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new task for the user

        Args:
            user_id: User ID
            title: Task title
            description: Task description (optional)
            priority: Task priority (optional)
            due_date: Task due date (optional)

        Returns:
            Dictionary with task details
        """
        try:
            # Create task
            task = Task(
                id=uuid.uuid4(),
                user_id=user_id,
                title=title,
                description=description or "",
                completed=False,
                priority=priority or "medium",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            if due_date:
                try:
                    task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except:
                    pass  # Skip invalid due dates

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "message": f"Task '{title}' added successfully"
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add task: {str(e)}"
            }

    def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as completed

        Args:
            user_id: User ID
            task_id: Task ID to complete

        Returns:
            Dictionary with result
        """
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = self.session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found or access denied"
                }

            # Update task
            task.completed = True
            task.updated_at = datetime.utcnow()
            self.session.add(task)
            self.session.commit()

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' marked as completed"
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete task: {str(e)}"
            }

    def list_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        List tasks for the user

        Args:
            user_id: User ID
            completed: Filter by completion status (optional)
            limit: Maximum number of tasks to return

        Returns:
            Dictionary with task list
        """
        try:
            # Build query
            statement = select(Task).where(Task.user_id == user_id)

            if completed is not None:
                statement = statement.where(Task.completed == completed)

            statement = statement.order_by(Task.created_at.desc()).limit(limit)

            # Execute query
            tasks = self.session.exec(statement).all()

            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "message": f"Found {len(task_list)} tasks"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list tasks: {str(e)}"
            }

    def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a task

        Args:
            user_id: User ID
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with result
        """
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = self.session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found or access denied"
                }

            # Update fields
            if title:
                task.title = title
            if description:
                task.description = description
            if priority:
                task.priority = priority
            if due_date:
                try:
                    task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except:
                    pass

            task.updated_at = datetime.utcnow()
            self.session.add(task)
            self.session.commit()

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' updated successfully"
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update task: {str(e)}"
            }

    def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Delete a task

        Args:
            user_id: User ID
            task_id: Task ID to delete

        Returns:
            Dictionary with result
        """
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = self.session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "message": f"Task not found or access denied"
                }

            task_title = task.title
            self.session.delete(task)
            self.session.commit()

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{task_title}' deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete task: {str(e)}"
            }
