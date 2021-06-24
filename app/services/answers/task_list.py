"""Helpers for building bot answer messages in task list."""
from typing import Optional

from botx import File, Message, MessageMarkup, SendingMessage

from app.bot.commands.listing import CommandsEnum
from app.resources import strings
from app.schemas.task import Task


def get_commands_help_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.COMMANDS_HELP_TEXT, message=message
    )

    answer.add_bubble(
        command=CommandsEnum.CREATE_TASK.command,
        label=strings.CREATE_TASK_LABEL,
    )
    answer.add_bubble(
        command=CommandsEnum.TASK_LIST.command,
        label=strings.TASK_LIST_LABEL,
    )

    return answer


def get_task_list_count_message(message: Message, count: int) -> SendingMessage:
    text = strings.TASK_LIST_COUNT_TEXT.format(
        count=count,
    )

    return SendingMessage.from_message(text=text, message=message)


def get_task_message(message: Message, task: Task) -> SendingMessage:
    text = strings.TASK_LIST_TEXT.format(
        title=task.title,
        description=task.description,
    )
    answer = SendingMessage.from_message(text=text, message=message)
    if task.assignee:
        answer.mention_contact(task.assignee)

    answer.add_bubble(
        command=CommandsEnum.EXPAND_TASK.command,
        label=strings.EXPAND_TASK_LABEL,
        data={"task_id": task.id},
    )

    return answer


def get_empty_task_list_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.EMPTY_TASK_LIST_TEXT, message=message
    )
    answer.add_bubble(
        command=CommandsEnum.CREATE_TASK.command,
        label=strings.CREATE_TASK_LABEL,
    )

    return answer


def get_full_task_description_message(
    message: Message, task: Task, markup: Optional[MessageMarkup] = None
) -> SendingMessage:
    text = strings.EXPAND_TASK_MESSAGE.format(
        title=task.title,
        description=task.description,
    )

    answer = SendingMessage.from_message(text=text, message=message)
    if task.assignee:
        answer.mention_contact(task.assignee)
    if markup:
        answer.markup = markup

    return answer


def get_full_task_description_markup(
    message: Message,
    task: Task,
) -> MessageMarkup:
    answer = SendingMessage.from_message(message=message)

    answer.add_bubble(
        command=CommandsEnum.EDIT_TASK.command,
        label=strings.EDIT_TASK_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.DELETE_TASK.command,
        label=strings.DELETE_TASK_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.TASK_LIST.command,
        label=strings.TASK_LIST_LABEL,
    )

    return answer.markup


def get_attachment_with_markup_message(
    message: Message, attachment: File, markup: Optional[MessageMarkup] = None
) -> SendingMessage:
    answer = SendingMessage.from_message(message=message)
    answer.add_file(attachment)
    if markup:
        answer.markup = markup

    return answer
