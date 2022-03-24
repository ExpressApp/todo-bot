from uuid import UUID

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql

from app.db.sqlalchemy import Base


class AttachmentModel(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    file_storage_uuid: UUID = Column(postgresql.UUID(as_uuid=True))
    filename: str = Column(String)
    