from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid
from db.base import Base


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(SQLModel):
    """Base fields for Task model"""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    due_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(index=True)  # Indexed for efficient user-based queries


class Task(TaskBase, table=True):
    """Task model with database table configuration"""
    __tablename__ = "tasks"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"default": datetime.utcnow, "onupdate": datetime.utcnow})


class TaskCreate(SQLModel):
    """Schema for creating a new task"""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    due_date: Optional[datetime] = Field(default=None)
    # Note: user_id will be set automatically from authenticated user


class TaskRead(TaskBase):
    """Schema for reading a task"""
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]


class TaskUpdate(SQLModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[PriorityEnum] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)