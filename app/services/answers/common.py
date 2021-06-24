"""Helpers for building bot answer messages."""
from botx import Message, SendingMessage
from loguru import logger

from app.bot.commands.listing import CommandsEnum
from app.resources import strings


def default_message(message: Message) -> SendingMessage:

    answer = SendingMessage.from_message(
        text=strings.DEFAULT_MESSAGE_TEXT, message=message
    )

    answer.add_bubble(
        label="Создать задачу",
        command=CommandsEnum.CREATE_TASK.command,
    )
    answer.add_bubble(
        label="Посмотреть список задач",
        command=CommandsEnum.TASK_LIST.command,
    )
    return answer


def chat_created_message(message: Message) -> SendingMessage:
    """Build message which should be send to chat with new user."""
    logger.bind(botx_bot=True, payload=message).warning("CREATE_CHAT")

    answer = SendingMessage.from_message(
        text=strings.CHAT_CREATED_TEXT, message=message
    )

    answer.add_bubble(
        label="Создать задачу",
        command=CommandsEnum.CREATE_TASK.command,
    )
    return answer
