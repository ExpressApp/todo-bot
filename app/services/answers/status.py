from typing import Optional, Union
from botx import BubbleMarkup, IncomingMessage, OutgoingMessage

from app.resources.strings import CREATE_TASK_LABEL, LIST_TASKS_LABEL


def get_status_message(message: IncomingMessage, title: Optional[str]=None) -> OutgoingMessage:
    body = [
        f"**{title}**\n\n" if title else "",
        "Для дальнейшей работы нажмите любую из кнопок ниже:"
    ]

    bubbles = BubbleMarkup()
    bubbles.add_button(command="/создать", label=CREATE_TASK_LABEL)
    bubbles.add_button(command="/список", label=LIST_TASKS_LABEL)

    return OutgoingMessage(
        bot_id=message.bot.id, 
        chat_id=message.chat.id, 
        body="".join(body), 
        bubbles=bubbles,
    )
