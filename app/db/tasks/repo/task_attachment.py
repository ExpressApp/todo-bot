"""Task Attachment repository."""

from typing import Optional
from uuid import UUID

from botx import File
from botx.models.files import BOTX_API_ACCEPTED_EXTENSIONS
from tortoise.exceptions import DoesNotExist

from app.db.tasks.models import AttachmentModel
from app.schemas.task import TaskAttachment
from app.services.file_storage import FileStorage


class TaskAttachmentRepo:
    def __init__(self, file_storage: FileStorage) -> None:
        """Init file storage."""
        self._file_storage = file_storage

    async def create_attachment(self, attachment: File) -> TaskAttachment:
        """Save file content to file storage and save file metadata to database."""
        if attachment.file_name.endswith(tuple(BOTX_API_ACCEPTED_EXTENSIONS)):
            file_storage_uuid = await self._file_storage.save(attachment=attachment)

            task_attachment_meta = await AttachmentModel.create(
                id=file_storage_uuid, filename=attachment.file_name
            )

            return TaskAttachment(
                id=task_attachment_meta.id,
                filename=task_attachment_meta.filename,
                _file_storage=self._file_storage,
            )
        raise ValueError

    async def remove_attachment(self, attachment_id: UUID) -> None:
        """Remove attachment from file storage."""
        try:
            task_attachment_meta = await AttachmentModel.get(id=attachment_id)
        except DoesNotExist:
            return None
        await task_attachment_meta.delete()
        await self._file_storage.remove(task_attachment_meta.id)

    async def get_attachment_by_id(
        self,
        attachment_id: UUID,
    ) -> Optional[File]:
        """Get attachment from file storage."""
        try:
            attachment_model = await AttachmentModel.get(id=attachment_id)
        except DoesNotExist:
            return None
        return await self._file_storage.get_file(
            attachment_model.id, attachment_model.filename
        )
