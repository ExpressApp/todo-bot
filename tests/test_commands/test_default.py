from typing import Awaitable, Callable

from botx import Bot, BubbleMarkup, IncomingMessage, StatusRecipient
from botx.models.commands import BotCommand

from app.resources import strings


async def test_default_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Act -
    await execute_bot_command(bot, message)

    # - Assert -
    bubbles = BubbleMarkup()
    bubbles.add_button(command="/создать", label=strings.CREATE_TASK_LABEL)
    bubbles.add_button(command="/список", label=strings.LIST_TASKS_LABEL)
    
    bot.answer_message.assert_awaited_once_with(
        body=strings.DEFAULT_MESSAGE,
        bubbles=bubbles,
    )


async def test_help_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/help")

    status_recipient = StatusRecipient.from_incoming_message(message)

    status = await bot.get_status(status_recipient)
    command_map = dict(sorted(status.items()))

    answer_body = "\n".join(
        f"`{command}` -- {description}" for command, description in command_map.items()
    )

    # - Act -
    await execute_bot_command(bot, message)
    
    # - Assert -
    bot.answer_message.assert_awaited_once_with(answer_body)
    