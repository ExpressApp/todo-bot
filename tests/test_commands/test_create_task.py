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
from pybotx.models.message.mentions import MentionContact
import pytest


@pytest.fixture
def contact() -> MentionContact:
    return MentionBuilder.contact(uuid4())


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
    contact: MentionContact,
    incoming_attachment: AttachmentDocument,
    fsm_session: None,
    bot_id: UUID,
) -> None:
    # - Arrange -
    start_creating_task_message = incoming_message_factory(body="/создать")
    send_title_message = incoming_message_factory(body="Title")
    send_description_message = incoming_message_factory(body="Description")
    send_mentions_message = incoming_message_factory(
        body=str(contact), mentions=MentionList([contact])
    )
    send_attachment_message = incoming_message_factory(attachment=incoming_attachment)
    send_confirm_message = incoming_message_factory(body="YES")

    # - Act -
    async with lifespan_wrapper(bot):
        await bot.async_execute_bot_command(start_creating_task_message)
        await bot.async_execute_bot_command(send_title_message)
        await bot.async_execute_bot_command(send_description_message)
        await bot.async_execute_bot_command(send_mentions_message)
        await bot.async_execute_bot_command(send_attachment_message)
        await bot.async_execute_bot_command(send_confirm_message)

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
