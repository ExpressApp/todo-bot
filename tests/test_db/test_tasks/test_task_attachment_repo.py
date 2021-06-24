from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from botx import File

from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.services.file_storage import FileStorage


@pytest.fixture
def file_storage_mock(file_uuid: UUID) -> AsyncMock:
    file_storage = AsyncMock()
    file_storage.save.return_value = file_uuid
    file_storage.remove.return_value = None
    file_storage.get_file.return_value = file_uuid
    return file_storage


@pytest.fixture
def task_attachment_repo(file_storage_mock: FileStorage) -> TaskAttachmentRepo:
    return TaskAttachmentRepo(file_storage_mock)


@pytest.mark.asyncio
async def test_create_attachment(
    file: File, file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    attachment = await task_attachment_repo.create_attachment(file)
    assert attachment.id == file_uuid


@pytest.mark.asyncio
async def test_create_attachment_extension_error(
    file: File, file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    file.file_name = "wrong_extension.md"
    with pytest.raises(ValueError) as e:
        await task_attachment_repo.create_attachment(file)
    assert e.type == ValueError


@pytest.mark.asyncio
async def test_get_attachment(
    file: File, file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    await task_attachment_repo.create_attachment(file)
    assert await task_attachment_repo.get_attachment_by_id(file_uuid) == file_uuid


@pytest.mark.asyncio
async def test_get_attachment_not_exist_error(
    file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    task = await task_attachment_repo.get_attachment_by_id(file_uuid)
    assert task is None


@pytest.mark.asyncio
async def test_remove_attachment(
    file: File, file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    await task_attachment_repo.create_attachment(file)
    await task_attachment_repo.remove_attachment(file_uuid)
    assert await task_attachment_repo.get_attachment_by_id(file_uuid) is None


@pytest.mark.asyncio
async def test_remove_attachment__not_exist_error(
    file: File, file_uuid: UUID, task_attachment_repo: TaskAttachmentRepo
):
    result = await task_attachment_repo.remove_attachment(file_uuid)
    assert result is None
