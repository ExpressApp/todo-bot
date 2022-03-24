from dataclasses import dataclass
from uuid import UUID


@dataclass
class Attachment:
    id: int
    file_storage_id: UUID
    filename: str
    