"""Attachment repo."""

from app.db.attachment.models import AttachmentModel
from app.db.crud import CRUD
from app.db.sqlalchemy import AsyncSession
from app.schemas.attachments import Attachment, AttachmentInCreation


class AttachmentRepo:
    def __init__(self, session: AsyncSession):
        self._crud = CRUD(session=session, cls_model=AttachmentModel)

    async def create_attachment(
        self, attachment_in_creation: AttachmentInCreation
    ) -> Attachment:
        row = await self._crud.create(
            model_data={
                "file_storage_id": attachment_in_creation.file_storage_id,
                "filename": attachment_in_creation.filename,
                "task_id": attachment_in_creation.task_id,
            },
        )
        attachment_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(attachment_in_db)

    def _to_domain(self, attachment_in_db: AttachmentModel) -> Attachment:
        return Attachment(
            id=attachment_in_db.id,
            file_storage_id=attachment_in_db.file_storage_id,
            filename=attachment_in_db.filename,
            task_id=attachment_in_db.task_id,
        )
