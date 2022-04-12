import asyncio
from typing import Callable
from uuid import UUID, uuid4

from botx import (
    AttachmentTypes, 
    Bot,
    IncomingMessage,
    Mention, 
    lifespan_wrapper
)
from botx.models.attachments import AttachmentDocument
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.caching.redis_repo import RedisRepo

from app.interactors.create_task import CreateTaskInteractor
from app.schemas.attachments import AttachmentInCreation
from app.schemas.tasks import Task, TaskInCreation


@pytest.fixture
def incoming_attachment() -> AttachmentDocument:
    return AttachmentDocument(
        type=AttachmentTypes.DOCUMENT,
        filename="text.txt",
        size=len(b"Hello, world!"),
        is_async_file=False,
        content=b"Hello, world!"
    )


@pytest.fixture
def task_in_creation() -> TaskInCreation:
    return TaskInCreation(
        user_huid=UUID('bfe69a39-6b0a-4d8b-b2df-b8ca7955ec75'),
        title="Title",
        description="Description",
        mentioned_colleague_id=UUID('eecbb10f-e77e-44a4-aa96-69c9010b882b')
    )


@pytest.fixture
def attachment_in_creation() -> AttachmentInCreation:
    return AttachmentInCreation(
        file_storage_id=UUID('1aaafa13-3210-4908-98ab-9d8cb5245b9f'),
        filename="test.txt",
        task_id=1
    )


@pytest.fixture
def task() -> Task:
    return Task(
        id=1,
        user_huid=UUID('bfe69a39-6b0a-4d8b-b2df-b8ca7955ec75'),
        title="Title",
        description="Description",
        mentioned_colleague_id=UUID('eecbb10f-e77e-44a4-aa96-69c9010b882b'),
        attachment=None
    )


@pytest.mark.db
async def test_task_creation(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    db_session: AsyncSession,
    task_in_creation: TaskInCreation,
    attachment_in_creation: AttachmentInCreation,
    task: Task,
    redis_repo: RedisRepo,
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")

    contact = Mention.contact(huid=uuid4())
    contact_message = incoming_message_factory(body=str(contact))

    file_message = incoming_message_factory()
    file_message.file = incoming_attachment

    confirm_message = incoming_message_factory(body="YES")

    messages = [
        command_message, title_message, description_message,
        contact_message, file_message, confirm_message,
    ]

    # - Act -
    async with lifespan_wrapper(bot):
        for message in messages:
            bot.async_execute_bot_command(message)
            await asyncio.sleep(0.5)
        await redis_repo.delete(
            await redis_repo.get("fsm:*2c7f7a5e-f2fd-45c4-b0f1-453ed2f34fad*")
        )

    interactor = CreateTaskInteractor(db_session)

    # - Assert -
    assert (await interactor.execute(task_in_creation, attachment_in_creation)) == task
