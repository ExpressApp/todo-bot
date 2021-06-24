from pathlib import Path
from uuid import UUID

import pytest
from botx import File

from app.services.file_storage import FileStorage
from app.settings.config import get_app_settings


@pytest.fixture
def file_storage() -> FileStorage:
    config = get_app_settings()
    return FileStorage(config.FILE_STORAGE_PATH)


@pytest.mark.asyncio
def test_file_storage_path_not_exist():
    with pytest.raises(FileNotFoundError) as e:
        FileStorage(Path("/wrong/path/"))
    assert e.type == FileNotFoundError


@pytest.mark.asyncio
async def test_save_file(
    file: File,
    file_storage: FileStorage,
):
    file_uuid = await file_storage.save(file)
    assert file_uuid is not None


@pytest.mark.asyncio
async def test_get_file(
    file: File,
    file_storage: FileStorage,
):
    file_uuid = await file_storage.save(file)
    file_from_storage = await file_storage.get_file(file_uuid, "test.txt")
    assert file == file_from_storage


@pytest.mark.asyncio
async def test_get_file_not_exist_error(
    file_uuid: UUID,
    file_storage: FileStorage,
):
    with pytest.raises(FileNotFoundError) as e:
        await file_storage.get_file(file_uuid, "test.txt")
    assert e.type == FileNotFoundError


@pytest.mark.asyncio
async def test_remove_file(
    file: File,
    file_storage: FileStorage,
):
    file_uuid = await file_storage.save(file)
    await file_storage.remove(file_uuid)
    with pytest.raises(FileNotFoundError):
        assert await file_storage.get_file(file_uuid, "test.txt") == None


@pytest.mark.asyncio
async def test_remove_file_not_exist_error(
    file_uuid: UUID,
    file_storage: FileStorage,
):
    with pytest.raises(FileNotFoundError) as e:
        await file_storage.remove(file_uuid)
    assert e.type == FileNotFoundError
