from typing import Awaitable, Callable

from botx import Bot, BubbleMarkup, Button, IncomingMessage
from botx.models.commands import BotCommand


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
    bot.answer_message.assert_awaited_once_with(
        body=(
            "К сожалению, мне не удалось найти информацию.\n\n"
            "С моей помощью вы сможете работать со списками задач, " 
            "чтобы контролировать дела, которые нужно сделать за день.\n\n"
            "Для дальнейшей работы нажмите на одну из кнопок ниже:"
        ),
        bubbles=BubbleMarkup(
            [
                [Button(command="/создать", label="Создать задачу")],
                [Button(command="/список", label="Показать список задач")]
            ]
        ),
    )


async def test_help_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/help")

    # - Act -
    await execute_bot_command(bot, message)
    
    # - Assert -
    bot.answer_message.assert_awaited_once_with(
        (
            "`/help` -- Get available commands\n"
            "`/создать` -- Создать новую задачу\n"
            "`/список` -- Посмотреть список задач"
        )
    )
    