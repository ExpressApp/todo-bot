"""Schemas for DB models."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.services.file_storage import FileStorage


class TaskInCreation(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[UUID] = None
    attachment: Optional[UUID] = None

    class Config:
        validate_assignment = True


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[UUID] = None
    attachment_id: Optional[UUID] = None

    class Config:
        orm_mode = True


class TaskAttachment(BaseModel):
    id: UUID
    filename: str

    _file_storage: FileStorage
