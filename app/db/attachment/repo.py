from aiofiles.tempfile.temptypes import AsyncSpooledTemporaryFile

from app.db.attachment.models import AttachmentModel
from app.db.crud import CRUD
from app.db.sqlalchemy import AsyncSession
from app.schemas.attachments import Attachment
from app.services.file_storage import FileStorage


class AttachmentRepo:
    
    def __init__(self, file_storage: FileStorage, session: AsyncSession):
        self._crud = CRUD(session=session, cls_model=AttachmentModel)
        self._file_storage = file_storage

    async def create_attachment(
        self, 
        file: AsyncSpooledTemporaryFile, 
        filename: str
    ) -> Attachment:
        file_storage_id = await self._file_storage.save(file)
        
        row = await self._crud.create(
            model_data={"file_storage_id": file_storage_id, "filename": filename},
        )
        attachment_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(attachment_in_db)


    async def get_attachment_name(self, attachment_id: int) -> str:
        pass

    async def remove_attachment(self, attachment_id: int) -> None:
        pass

    def _to_domain(self, attachment_in_db: AttachmentModel) -> Attachment:
        pass
