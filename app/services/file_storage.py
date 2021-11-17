"""Storage for saving and reading files."""
import io
from pathlib import Path
from uuid import UUID, uuid4

from aiofiles import os as async_os
from botx import File

from app.settings.config import get_app_settings


class FileStorage:
    def __init__(self, storage_path: Path) -> None:
        """Create new file storage.

        `storage_path` should be path to existing directory.
        """

        if storage_path.exists():
            self._storage_path = storage_path
        else:
            raise FileNotFoundError

    async def get_file(self, file_uuid: UUID, attachment_name: str) -> File:
        """Get file object in storage by its UUID."""

        file_path = self._get_path_to_file(file_uuid)
        if file_path.exists():
            with open(file_path, "rb") as fo:
                file_bytes = fo.read()
            file_io = io.BytesIO(file_bytes)
            return File.from_file(file=file_io, filename=attachment_name)
        raise FileNotFoundError

    async def save(self, attachment: File) -> UUID:
        """Save file to storage using its file object.

        Returns file UUID.
        """

        file_uuid = uuid4()
        file_path = self._get_path_to_file(file_uuid)

        with open(file_path, "wb") as target_fo:
            target_fo.write(attachment.file.read())

        return file_uuid

    async def remove(self, file_uuid: UUID) -> None:
        """Remove file from storage file uuid."""

        file_path = self._get_path_to_file(file_uuid)

        if file_path.exists():
            await async_os.remove(file_path)
        else:
            raise FileNotFoundError

    def _get_path_to_file(self, file_uuid: UUID) -> Path:
        return self._storage_path.joinpath(str(file_uuid))


config = get_app_settings()
file_storage = FileStorage(config.FILE_STORAGE_PATH)
