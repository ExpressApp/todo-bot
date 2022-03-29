from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Task:
    id: int
    user_huid: UUID
    title: str
    description: str
    mentioned_colleague_id: Optional[UUID]
    attachment_id: Optional[int]


@dataclass
class TaskInCreation:
    user_huid: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    mentioned_colleague_id: Optional[UUID] = None
    attachment_id: Optional[int] = None
