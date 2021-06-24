"""Helpers for building bot answer messages for case of forward message."""

from botx import Message, SendingMessage

from app.bot.commands.listing import FSMCommandsEnum
from app.resources import strings


def get_decision_create_task_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.DECISION_CREATE_TASK_MESSAGE, message=message
    )

    answer.add_bubble(
        command=FSMCommandsEnum.YES, label=strings.YES_LABEL, new_row=False
    )
    answer.add_bubble(command=FSMCommandsEnum.NO, label=strings.NO_LABEL)

    return answer


def get_as_title_or_description_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.AS_TITLE_OR_DESCRIPTION, message=message
    )
    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    answer.add_bubble(
        command=FSMCommandsEnum.MESSAGE_AS_TITLE,
        label=strings.AS_TITLE_LABEL,
        new_row=False,
    )
    answer.add_bubble(
        command=FSMCommandsEnum.MESSAGE_AS_DESCRIPTION,
        label=strings.AS_DESCRIPTION_LABEL,
    )

    return answer


def get_text_when_command_required_message(message: Message) -> SendingMessage:
    answer = SendingMessage.from_message(
        text=strings.TEXT_WHEN_COMMAND_REQUIRED_ERROR, message=message
    )

    answer.add_keyboard_button(
        command=FSMCommandsEnum.CANCEL_PROCESS, label=strings.CANCEL_LABEL
    )

    return answer
