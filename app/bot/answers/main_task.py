"""Message with expanded task builder."""

from pybotx import IncomingMessage, MentionBuilder, OutgoingMessage

from app.bot.answers.control_bubbles import build_task_control_bubbles
from app.schemas.tasks import Task


def build_main_task_messages(
    message: IncomingMessage,
    task: Task,
    has_attachment: bool,
) -> OutgoingMessage:
    colleague_id = task.mentioned_colleague_id
    contact = MentionBuilder.contact(colleague_id) if colleague_id else "Без контакта"

    message = OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=f"**{task.title}**\n\n{task.description}\n\n**Контакт:** {contact}",
    )

    if not has_attachment:
        message.bubbles = build_task_control_bubbles(task.id)

    return message
