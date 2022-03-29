from botx import BubbleMarkup, IncomingMessage, Mention, OutgoingMessage
from app.schemas.attachments import AttachmentInCreation
from app.schemas.enums import StrEnum
from app.schemas.tasks import TaskInCreation

from app.services.buttons.cancel import get_cancel_keyboard_button


def get_task_approve_message(
    message: IncomingMessage,
    task: TaskInCreation,
    attachment: AttachmentInCreation,
    commands: StrEnum
) -> OutgoingMessage:
    contact = "Без контакта"
    if task.mentioned_colleague_id:
        contact = Mention.contact(huid=task.mentioned_colleague_id)

    file = "Без вложения"
    if attachment.filename:
        file = attachment.filename

    text = '\n'.join([
        f"**Название задачи**: {task.title}",
        f"**Описание задачи**: {task.description}",
        f"**Контакт**: {contact}\n",
        f"**Вложение**: {file}\n\n"
    ])

    bubbles = BubbleMarkup()
    bubbles.add_button(command=commands.YES, label="Да")
    bubbles.add_button(command=commands.NO, label="Нет")

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=text,
        bubbles=bubbles,
        keyboard=get_cancel_keyboard_button()
    )