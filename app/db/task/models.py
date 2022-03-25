from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.sqlalchemy import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_huid: UUID = Column(postgresql.UUID(as_uuid=True))
    title: str = Column(String)
    description: str = Column(String)
    mentioned_colleague_id: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), nullable=True)
    attachment_id: Optional[int] = Column(Integer, ForeignKey('attachments.id'), nullable=True, unique=True)
