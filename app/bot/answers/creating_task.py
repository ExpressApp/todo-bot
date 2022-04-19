"""Helpers for building bot answer messages in the process of creating a task."""

import inspect
from functools import wraps
from typing import Any, Callable

from botx import Message, SendingMessage

from app.bot.commands.listing import CommandsEnum, FSMCommandsEnum
from app.resources import strings
from app.schemas.task import TaskInCreation


# Add skip bubble if function was called from 'creating_task.py' (for service screens)
def skip_bubble(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self: Any) -> SendingMessage:  # noqa: WPS430
        answer = func(self)
        file_from_call = inspect.getouterframes(inspect.currentframe())[
            1
        ].filename.split("/")[-1]
        if file_from_call == "creating_task.py":
            answer.add_bubble(
                command=FSMCommandsEnum.SKIP_INPUT, label=strings.SKIP_INPUT_LABEL
            )
        return answer

    return wrapper


def get_cancel_task_creation_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.CANCEL_TASK_CREATION_TEXT, message=message
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


def get_input_title_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(text=strings.INPUT_TITLE_TEXT, message=message)
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_input_description_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.INPUT_DESCRIPTION_TEXT, message=message
    )
    answer.add_bubble(
        command=FSMCommandsEnum.SKIP_INPUT, label=strings.SKIP_INPUT_LABEL
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_input_mention_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.INPUT_MENTION_TEXT, message=message
    )
    answer.add_bubble(
        command=FSMCommandsEnum.SKIP_INPUT, label=strings.SKIP_INPUT_LABEL
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_input_attachment_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.INPUT_ATTACHMENT_TEXT, message=message
    )
    answer.add_bubble(
        command=FSMCommandsEnum.SKIP_INPUT, label=strings.SKIP_INPUT_LABEL
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_checking_data_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(text=strings.CHECKING_DATA_TEXT, message=message)


def get_re_checking_data_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.RE_CHECKING_DATA_TEXT, message=message
    )


def get_full_task_description_message(
    message: Message, task: TaskInCreation
) -> SendingMessage:
    if message.attachments.all_attachments:
        file_name = message.attachments.file.file_name
    else:
        file_name = ""

    text = strings.FULL_TASK_DESCRIPTION_TEMPLATE.format(
        title=task.title,
        description=task.description,
        attachment_name=file_name,
    )
    answer = SendingMessage.from_message(text=text, message=message)
    if task.assignee:
        answer.mention_contact(task.assignee)
    answer.add_bubble(
        command=FSMCommandsEnum.YES, label=strings.YES_LABEL, new_row=False
    )

    answer.add_bubble(command=FSMCommandsEnum.NO, label=strings.NO_LABEL)

    return answer


def get_success_creating_task_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.SUCCESSFUL_CREATING_TASK_TEXT, message=message
    )
    answer.add_bubble(
        command=CommandsEnum.CREATE_TASK.command,
        label=strings.CREATE_TASK_LABEL,
    )
    answer.add_bubble(
        command=CommandsEnum.TASK_LIST.command, label=strings.TASK_LIST_LABEL
    )

    return answer


# Service screens
def get_file_when_title_required_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.FILE_WHEN_TITLE_REQUIRED_ERROR, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


@skip_bubble
def get_file_when_description_required_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.FILE_WHEN_DESCRIPTION_REQUIRED_ERROR, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )
    return answer


@skip_bubble
def get_mention_validation_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.MENTION_VALIDATION_ERROR, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )
    return answer


@skip_bubble
def get_attachment_not_support_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.ATTACHMENT_NOT_SUPPORT_TEXT, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )
    return answer


@skip_bubble
def get_text_when_file_required_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.TEXT_WHEN_FILE_REQUIRED_ERROR, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )
    return answer
