import asyncio
from typing import Awaitable, Callable

from botx import AttachmentTypes, Bot, BubbleMarkup, Button, IncomingMessage, KeyboardMarkup, lifespan_wrapper
from botx.models.attachments import AttachmentDocument
from botx.models.commands import BotCommand


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
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    command_message = incoming_message_factory(body="/создать")
    
    file_message = incoming_message_factory()
    file_message.file = AttachmentDocument(
        type=AttachmentTypes.DOCUMENT,
        filename="test.txt",
        size=len(b"Hello, world!\n"),
        is_async_file=False,
        content=b"Hello, world!\n",
    )

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
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
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
