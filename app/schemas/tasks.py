from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from .attachments import Attachment


@dataclass
class Task:
    id: int
    user_huid: UUID
    title: str
    description: str
    mentioned_colleague_id: Optional[UUID]
    attachment_id: Optional[int]
