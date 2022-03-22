from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Attachment:
    id: int
    file_storage_id: UUID
    filename: str


@dataclass
class Task:
    id: int
    user_huid: UUID
    title: str
    description: str
    mentioned_colleague: Optional[UUID]
    attachment: Optional[Attachment]
