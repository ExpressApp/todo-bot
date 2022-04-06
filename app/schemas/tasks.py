from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.schemas.attachments import Attachment


@dataclass
class Task:
    id: int
    user_huid: UUID
    title: str
    description: str
    mentioned_colleague_id: Optional[UUID]
    attachment: Optional[Attachment] = None


@dataclass
class TaskInCreation:
    user_huid: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    mentioned_colleague_id: Optional[UUID] = None
