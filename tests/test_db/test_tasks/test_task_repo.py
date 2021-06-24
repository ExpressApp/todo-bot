from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from botx import File

from app.db.tasks.repo.task import TaskRepo
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import Task, TaskInCreation
from app.services.file_storage import FileStorage


@pytest.fixture
def task(bot_id: UUID, file_uuid: UUID) -> TaskInCreation:
    return TaskInCreation(
        title="test title",
        description="test description",
        assignee=bot_id,
        attachment=file_uuid,
    )


@pytest.fixture
def file_storage_mock(file_uuid: UUID) -> AsyncMock:
    file_storage = AsyncMock()
    file_storage.save.return_value = file_uuid
    file_storage.remove.return_value = None
    file_storage.get_file.return_value = file_uuid
    return file_storage


@pytest.fixture
async def task_attachment_repo(
    file: File, file_storage_mock: FileStorage
) -> TaskAttachmentRepo:
    task_attachment_repo_entity = TaskAttachmentRepo(file_storage_mock)
    await task_attachment_repo_entity.create_attachment(file)
    return task_attachment_repo_entity


@pytest.fixture
def task_repo(task_attachment_repo: TaskAttachmentRepo) -> TaskRepo:
    return TaskRepo(task_attachment_repo)


@pytest.mark.asyncio
async def test_create_task(task: TaskInCreation, task_repo: TaskRepo):
    task_from_db = await task_repo.create_task(task)
    assert task.title == task_from_db.title


@pytest.mark.asyncio
async def test_get_task(task: TaskInCreation, task_repo: TaskRepo):
    await task_repo.create_task(task)
    task_from_db = await task_repo.get_task_by_id(1)
    assert task.title == task_from_db.title


@pytest.mark.asyncio
async def test_get_task_not_exist_error(task_repo: TaskRepo):
    task_from_db = await task_repo.get_task_by_id(1)
    assert task_from_db is None


@pytest.mark.asyncio
async def test_delete_task(task: TaskInCreation, task_repo: TaskRepo):
    await task_repo.create_task(task)
    await task_repo.delete_task(1)
    task_from_db = await task_repo.get_task_by_id(1)
    assert task_from_db is None


@pytest.mark.asyncio
async def test_delete_task_not_exist_error(task: TaskInCreation, task_repo: TaskRepo):
    result = await task_repo.delete_task(1)
    assert result is None


@pytest.mark.asyncio
async def test_get_all_tasks(task: TaskInCreation, task_repo: TaskRepo):
    await task_repo.create_task(task)
    await task_repo.create_task(task)
    tasks_from_db = await task_repo.get_all_tasks()
    assert len(tasks_from_db) == 2


@pytest.mark.asyncio
async def test_edit_task(task: TaskInCreation, task_repo: TaskRepo):
    await task_repo.create_task(task)
    task.title = "new_test_title"
    task.assignee = None
    task.attachment = None
    await task_repo.edit_task(Task(id=1, **(task.dict())))
    tasks_from_db = await task_repo.get_task_by_id(1)
    assert (
        tasks_from_db.title == "new_test_title"
        and tasks_from_db.assignee is None
        and tasks_from_db.attachment_id is None
    )
