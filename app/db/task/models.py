from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.sqlalchemy import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_huid: UUID = Column(postgresql.UUID(as_uuid=True))
    title: str = Column(String)
    description: str = Column(String)
    mentioned_colleague: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), nullable=True)
    attachment_id: Optional[int] = Column(Integer, nullable=True, unique=True)

    attachment = relationship(
        "app.db.attachment.models.AttachmentModel",
        back_populates="tasks",
        uselist=False
    )
