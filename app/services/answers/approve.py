"""Approve message builder."""

from botx import BubbleMarkup, IncomingMessage, Mention, OutgoingMessage

from app.resources.strings import TASK_APPROVE
from app.schemas.attachments import AttachmentInCreation
from app.schemas.enums import TaskApproveCommands
from app.schemas.tasks import TaskInCreation
from app.services.buttons.cancel import get_cancel_keyboard_button


def get_task_approve_message(
    message: IncomingMessage, task: TaskInCreation, attachment: AttachmentInCreation
) -> OutgoingMessage:
    contact = "Без контакта"
    if task.mentioned_colleague_id:
        contact = Mention.contact(huid=task.mentioned_colleague_id)

    file = "Без вложения"
    if attachment.filename:
        file = attachment.filename

    text = TASK_APPROVE.format(
        title=task.title, description=task.description, contact=contact, file=file
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(command=TaskApproveCommands.YES, label="Да")
    bubbles.add_button(command=TaskApproveCommands.NO, label="Нет")

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=text,
        bubbles=bubbles,
        keyboard=get_cancel_keyboard_button(),
    )
