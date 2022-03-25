from uuid import UUID

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.sqlalchemy import Base


class AttachmentModel(Base):
    __tablename__ = "attachments"

    id: int = Column(Integer, ForeignKey('tasks.attachment_id', ondelete="CASCADE"), primary_key=True, autoincrement=True)
    file_storage_uuid: UUID = Column(postgresql.UUID(as_uuid=True))
    filename: str = Column(String)

    task = relationship(
        "app.db.task.models.TaskModel",
        back_populates="attachments"
    )
    