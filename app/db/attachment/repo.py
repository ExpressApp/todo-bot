from aiofiles.tempfile.temptypes import AsyncSpooledTemporaryFile

from app.db.sqlalchemy import AsyncSession
from app.schemas.attachments import Attachment
from app.services.file_storage import FileStorage


class AttachmentRepo:
    
    def __init__(self, file_storage: FileStorage, session: AsyncSession):
        pass

    async def create_attachment(
        self, 
        file: AsyncSpooledTemporaryFile, 
        filename: str
    ) -> Attachment:
        pass

    async def get_attachment_name(self, attachment_id: int) -> str:
        pass

    async def remove_attachment(self, attachment_id: int) -> None:
        pass
    
