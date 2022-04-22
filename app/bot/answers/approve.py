"""Approve message builder."""

from pybotx import BubbleMarkup, IncomingMessage, MentionBuilder, OutgoingMessage

from app.bot.answers.cancel import get_cancel_keyboard_button
from app.resources import strings
from app.schemas.attachments import AttachmentInCreation
from app.schemas.tasks import TaskInCreation


def get_task_approve_message(
    message: IncomingMessage, task: TaskInCreation, attachment: AttachmentInCreation
) -> OutgoingMessage:
    contact = "Без контакта"
    if task.mentioned_colleague_id:
        contact = MentionBuilder.contact(task.mentioned_colleague_id)

    file = "Без вложения"
    if attachment.filename:
        file = attachment.filename

    text = strings.TASK_APPROVE_TEMPLATE.format(
        title=task.title, description=task.description, contact=contact, file=file
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(command=strings.CONFIRM_TASK_COMMAND, label="Да")
    bubbles.add_button(command=strings.CANCEL_TASK_COMMAND, label="Нет")

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=text,
        bubbles=bubbles,
        keyboard=get_cancel_keyboard_button(),
    )
