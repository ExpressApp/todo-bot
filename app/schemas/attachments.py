from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Attachment:
    id: int
    file_storage_id: UUID
    filename: str
    task_id: int


@dataclass
class AttachmentInCreation:
    file_storage_id: Optional[UUID] = None
    filename: Optional[str] = None
    task_id: Optional[int] = None
