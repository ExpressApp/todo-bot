import asyncio
from typing import Awaitable, Callable
from uuid import uuid4

from botx import AttachmentTypes, Bot, BubbleMarkup, Button, IncomingMessage, KeyboardMarkup, Mention, MentionList, lifespan_wrapper
from botx.models.attachments import AttachmentDocument
from botx.models.commands import BotCommand
import pytest


@pytest.fixture
def incoming_attachment() -> AttachmentDocument:
    return AttachmentDocument(
        type=AttachmentTypes.DOCUMENT,
        filename="test.txt",
        size=len(b"Hello, world!\n"),
        is_async_file=False,
        content=b"Hello, world!\n",
    )


async def test_create_task_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/создать")

    # - Act -
    await execute_bot_command(bot, message)

    # - Assert -
    bot.answer_message.assert_awaited_once_with(
        body="Введите название задачи:",
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )


async def test_file_instead_title(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    
    file_message = incoming_message_factory()
    file_message.file = incoming_attachment

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(file_message)
        await asyncio.sleep(1)
        await file_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Чтобы указать **название** задачи, введите его **текстом**",
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )


async def test_task_title_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:

    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Введите текст задачи:",
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )

async def test_file_instead_description(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")

    file_message = incoming_message_factory()
    file_message.file = incoming_attachment

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(file_message)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Чтобы указать **описание** задачи, введите его **текстом**",
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )


async def test_description_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(description_message)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="При необходимости отметьте **одного коллегу**, связанного с задачей, через `@@`:",
        bubbles=BubbleMarkup(
            [
                [Button(command="SKIP", label="Пропустить")],
            ],
        ),
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )
    

async def test_wrong_contact(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")
    foo_mesage = incoming_message_factory(body="foo")

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(description_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(foo_mesage)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Вы некорректно отметили коллегу. Пожалуйста, укажите **только одного** пользователя **через @@**",
        bubbles=BubbleMarkup(
            [
                [Button(command="SKIP", label="Пропустить")],
            ],
        ),
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )

async def test_contact_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")
    
    contact = Mention.contact(huid=uuid4())
    contact_message = incoming_message_factory(body=str(contact))
    contact_message.mentions = MentionList([contact])

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(description_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(contact_message)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Прикрепите **вложение** (опционально):",
        bubbles=BubbleMarkup(
            [
                [Button(command="SKIP", label="Пропустить")],
            ],
        ),
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )


async def test_not_one_contact(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    title_message = incoming_message_factory(body="Title")
    description_message = incoming_message_factory(body="Description")
    
    first_contact = Mention.contact(huid=uuid4())
    second_contact = Mention.contact(huid=uuid4())
    contact_message = incoming_message_factory(
        body=" ".join([str(first_contact), str(second_contact)])
    )
    contact_message.mentions = MentionList([first_contact, second_contact])

    # - Act -
    async with lifespan_wrapper(bot):
        bot.async_execute_bot_command(command_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(title_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(description_message)
        await asyncio.sleep(1)
        bot.async_execute_bot_command(contact_message)
        await asyncio.sleep(1)
        await title_message.state.fsm.drop_state()

    # - Assert -
    bot.answer_message.assert_awaited_with(
        body="Вы некорректно отметили коллегу. Пожалуйста, укажите **только одного** пользователя **через @@**",
        bubbles=BubbleMarkup(
            [
                [Button(command="SKIP", label="Пропустить")],
            ],
        ),
        keyboard=KeyboardMarkup(
            [
                [Button(command="CANCEL", label="Отменить")],
            ]
        ),
    )
    