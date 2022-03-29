from dataclasses import dataclass
from fileinput import filename
from typing import Optional
from uuid import UUID


@dataclass
class Attachment:
    id: int
    file_storage_id: UUID
    filename: str
    
@dataclass
class AttachmentInCreation:
    file_storage_id: Optional[UUID] = None
    filename: Optional[str] = None
