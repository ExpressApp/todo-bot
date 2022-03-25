from uuid import UUID

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.sqlalchemy import Base


class AttachmentModel(Base):
    __tablename__ = "attachments"

    id: int = Column(Integer, primary_key=True)
    file_storage_id: UUID = Column(postgresql.UUID(as_uuid=True))
    filename: str = Column(String)
    