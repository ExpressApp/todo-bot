"""Helpers for building bot answer messages."""

from botx import Message, SendingMessage

from app.bot.commands.listing import CommandsEnum, FSMCommandsEnum
from app.resources import strings
from app.schemas.task import Task


def get_edit_task_message(message: Message, task: Task) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.EDIT_TASK_MESSAGE, message=message
    )

    answer.add_bubble(
        command=CommandsEnum.EDIT_TITLE.command,
        label=strings.EDIT_TITLE_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.EDIT_DESCRIPTION.command,
        label=strings.EDIT_DESCRIPTION_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.EDIT_MENTION.command,
        label=strings.EDIT_MENTION_IF_EXIST_LABEL
        if task.assignee
        else strings.EDIT_MENTION_IF_NOT_EXIST_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.EDIT_ATTACHMENT.command,
        label=strings.EDIT_ATTACHMENT_IF_EXIST_LABEL
        if task.attachment_id
        else strings.EDIT_ATTACHMENT_IF_NOT_EXIST_LABEL,
        data={"task_id": task.id},
    )

    answer.add_bubble(
        command=CommandsEnum.TASK_LIST.command,
        label=strings.RETURN_TO_TASK_LIST_LABEL,
    )

    return answer


def get_edit_title_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.EDIT_TITLE_MESSAGE, message=message
    )

    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_edit_description_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.EDIT_DESCRIPTION_MESSAGE, message=message
    )

    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_add_mention_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.ADD_MENTION_MESSAGE, message=message
    )

    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_add_attachment_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.ADD_ATTACHMENT_MESSAGE, message=message
    )

    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer


def get_successful_edit_title_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_EDIT_TITLE_MESSAGE, message=message
    )


def get_successful_edit_description_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_EDIT_DESCRIPTION_MESSAGE, message=message
    )


def get_successful_add_mention_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_ADD_MENTION_MESSAGE, message=message
    )


def get_successful_delete_mention_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_DELETE_MENTION_MESSAGE, message=message
    )


def get_successful_add_attachment_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_ADD_ATTACHMENT_MESSAGE, message=message
    )


def get_successful_delete_attachment_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.SUCCESSFUL_DELETE_ATTACHMENT_MESSAGE, message=message
    )


def get_cancel_edit_task_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.CANCEL_EDIT_TASK_TEXT, message=message
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


def get_delete_task_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.DELETE_TASK_MESSAGE, message=message
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


def get_must_push_button_for_editing_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(
        text=strings.MUST_PUSH_BUTTON_FOR_EDITING, message=message
    )


def task_not_exist_message(message: Message) -> SendingMessage:
    return SendingMessage.from_message(text=strings.TASK_NOT_EXIST, message=message)
