from botx import BubbleMarkup, IncomingMessage, Mention, OutgoingMessage
from app.schemas.enums import StrEnum

from app.services.buttons.cancel import cancel_keyboard_button


def get_task_approve_message(
    message: IncomingMessage,
    title: str,
    text: str,
    contact: Mention,
    filename: str,
    commands: StrEnum
) -> OutgoingMessage:
    contact_in_msg = contact if contact else "Без контакта"
    filename_in_msg = filename if filename else "Без вложения"
    text = (
        f"**Название задачи**: {title}\n"
        f"**Описание задачи**: {text}\n"
        f"**Контакт**: {contact_in_msg}\n"
        f"**Вложение**: {filename_in_msg}\n\n"
        "Все верно?\n\n"
    ).format(title=title, text=text, contact_in_msg=contact_in_msg, filename_in_msg=filename_in_msg)

    bubbles = BubbleMarkup()
    bubbles.add_button(command=commands.YES, label="Да")
    bubbles.add_button(command=commands.NO, label="Нет")

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=text,
        bubbles=bubbles,
        keyboard=cancel_keyboard_button()
    )