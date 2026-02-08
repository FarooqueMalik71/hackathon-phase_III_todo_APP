from sqlmodel import SQLModel
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class Base(SQLModel):
    """Base model with common configurations for all models"""

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override default dict method to exclude unset fields by default"""
        kwargs.setdefault("exclude_unset", True)
        return super().dict(**kwargs)

    class Config:
        """Pydantic configuration for the base model"""
        # Allow ORM mode for SQLModel compatibility
        from_attributes = True

        # Serialize datetime objects as ISO format strings
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }