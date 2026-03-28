"""Task data model for Notion integration."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskItem(BaseModel):
    """A task to be created in Notion."""
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    source_email_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
