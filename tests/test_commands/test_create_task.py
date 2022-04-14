from typing import Callable
from uuid import UUID, uuid4

from pybotx import (
    AttachmentTypes, 
    Bot,
    BubbleMarkup,
    Button,
    IncomingMessage,
    MentionBuilder,
    MentionList,
    OutgoingMessage, 
    lifespan_wrapper
)
from pybotx.models.attachments import AttachmentDocument
import pytest

from app.schemas.enums import TaskApproveCommands


@pytest.fixture
def incoming_attachment() -> AttachmentDocument:
    return AttachmentDocument(
        type=AttachmentTypes.DOCUMENT,
        filename="text.txt",
        size=len(b"Hello, world!"),
        is_async_file=False,
        content=b"Hello, world!"
    )


@pytest.mark.db
async def test_task_creation(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    fsm_session: None,
    bot_id: UUID,
) -> None:
    # - Arrange -

    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")

    contact = MentionBuilder.contact(uuid4())
    contact_message = incoming_message_factory(body=str(contact))
    contact_message.mentions = MentionList([contact])

    file_message = incoming_message_factory()
    file_message.file = incoming_attachment

    confirm_message = incoming_message_factory(body=TaskApproveCommands.YES)

    # - Act -
    async with lifespan_wrapper(bot):
        await bot.async_execute_bot_command(command_message)
        await bot.async_execute_bot_command(title_message)
        await bot.async_execute_bot_command(description_message)
        await bot.async_execute_bot_command(contact_message)
        await bot.async_execute_bot_command(file_message)
        await bot.async_execute_bot_command(confirm_message)

    # - Assert -
    bot.send.assert_awaited_with(
        message=OutgoingMessage(
            bot_id=bot_id,
            chat_id=UUID('a57aca87-e90b-4623-8bf2-9fb26adbdaaf'),
            body="**Задача успешно создана!**\n\n\nДля дальнейшей работы нажмите любую из кнопок ниже:",
            bubbles=BubbleMarkup(
                [
                    [Button(command="/создать", label="Создать задачу")],
                    [Button(command="/список", label="Показать список задач")],
                ],
            ),
        ),
    )
