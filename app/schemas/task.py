from uuid import UUID

from pydantic import BaseModel


class Task(BaseModel):
    id: int
    user_id: UUID
    title: str
    text: str
