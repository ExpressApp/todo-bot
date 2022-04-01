"""Storage for saving and reading files."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Protocol
from uuid import UUID, uuid4

import aiofiles
import aiofiles.os
from aiofiles.tempfile.temptypes import AsyncSpooledTemporaryFile
from botx.async_buffer import AsyncBufferReadable


class FileStorage:
    def __init__(self, storage_path: Path) -> None:
        """Create new file storage.

        `storage_path` should be path to existing directory.
        """

        assert storage_path.exists(), "`storage_path` dir should exists"

        self._storage_path = storage_path

    @asynccontextmanager
    async def file(self, file_uuid: UUID) -> AsyncIterator[AsyncBufferReadable]:
        """Get file object in storage by its UUID."""

        file_path = self._get_path_to_file(file_uuid)

        assert file_path.exists(), f"File with uuid {file_uuid} not exists"

        async with aiofiles.open(file_path, "rb") as fo:
            yield fo

    async def save(self, file: AsyncSpooledTemporaryFile) -> UUID:
        """Save file to storage using its file object.

        Returns file UUID.
        """

        file_uuid = uuid4()
        file_path = self._get_path_to_file(file_uuid)

        async with aiofiles.open(file_path, "wb") as target_fo:
            async for chunk in file:
                await target_fo.write(chunk)

        return file_uuid

    async def remove(self, file_uuid: UUID) -> None:
        file_path = self._get_path_to_file(file_uuid)

        assert file_path.exists(), f"File with uuid {file_uuid} not exists"

        await aiofiles.os.remove(file_path)

    def _get_path_to_file(self, file_uuid: UUID) -> Path:
        return self._storage_path.joinpath(str(file_uuid))
