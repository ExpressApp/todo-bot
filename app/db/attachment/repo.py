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
        file_storage_id = attachment_in_creation.file_storage_id
        filename = attachment_in_creation.filename

        row = await self._crud.create(
            model_data={"file_storage_id": file_storage_id, "filename": filename},
        )
        attachment_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(attachment_in_db)

    async def get_attachment(self, attachment_id: int) -> Attachment:
        attachment_in_db = await self._crud.get(pkey_val=attachment_id)
        return self._to_domain(attachment_in_db)

    async def remove_attachment(self, attachment_id: int) -> None:
        await self._crud.delete(pkey_val=attachment_id)

    def _to_domain(self, attachment_in_db: AttachmentModel) -> Attachment:
        return Attachment(
            id=attachment_in_db.id,
            file_storage_id=attachment_in_db.file_storage_id,
            filename=attachment_in_db.filename,
        )
