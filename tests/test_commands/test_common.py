from typing import Awaitable, Callable
from uuid import UUID

from pybotx import (
    Bot,
    BotAccount,
    BubbleMarkup,
    Button,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    IncomingMessage,
    UserKinds,
)
from pybotx.models.commands import BotCommand


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
    

async def test_chat_created_handler(
    bot: Bot,
    bot_id: UUID,
    host: str,
    execute_bot_command: Callable[[Bot, BotCommand], Awaitable[None]],
) -> None:
    # - Arrange -
    command = ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=bot_id,
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )

    # - Act -
    await execute_bot_command(bot, command)

    # - Assert -
    bot.answer_message.assert_awaited_once_with(
        (
            f"Вас приветствует ToDo bot!\n\n"
            "Для более подробной информации нажмите кнопку `/help`"
        ),
        bubbles=BubbleMarkup([[Button(command="/help", label="/help")]]),
    )
