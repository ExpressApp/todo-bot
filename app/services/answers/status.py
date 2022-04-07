"""Status message builder."""

from typing import Optional

from botx import BubbleMarkup, IncomingMessage, OutgoingMessage

from app.resources.strings import (
    CREATE_TASK_LABEL,
    LIST_TASKS_LABEL,
    TASK_STATUS_TEMPLATE,
)


def get_status_message(
    message: IncomingMessage, title: Optional[str] = None
) -> OutgoingMessage:
    body = TASK_STATUS_TEMPLATE.format(title=title)

    bubbles = BubbleMarkup()
    bubbles.add_button(command="/создать", label=CREATE_TASK_LABEL)
    bubbles.add_button(command="/список", label=LIST_TASKS_LABEL)

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="".join(body),
        bubbles=bubbles,
    )
