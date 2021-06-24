"""Widgets services."""

from typing import Optional, Union
from uuid import UUID, uuid4

from botx import (
    Bot,
    Message,
    MessageMarkup,
    MessageOptions,
    SendingCredentials,
    SendingMessage,
    UpdatePayload,
)


async def send_or_update_message(  # noqa: WPS231
    message: Message,
    bot: Bot,
    text: Optional[str],
    options: Optional[MessageOptions],
    markup: MessageMarkup = None,
    new_message_id: Union[str, UUID] = None,
) -> None:
    """Send new message or update exist."""

    current_message_id = message.data.get("message_id")
    new_message_id = new_message_id or uuid4()

    if markup:
        for bubbles in markup.bubbles:
            for bubble in bubbles:
                bubble.data["message_id"] = current_message_id or new_message_id
    else:
        markup = MessageMarkup()

    if current_message_id:
        payload = UpdatePayload(text=text)
        payload.set_markup(markup=markup)
        if options:
            payload.mentions = options.mentions
        await bot.update_message(
            SendingCredentials(
                sync_id=current_message_id, bot_id=message.bot_id, host=message.host
            ),
            update=payload,
        )
    else:
        message = SendingMessage.from_message(text=text, message=message)
        message.credentials.message_id = new_message_id
        message.markup = markup
        message.options = options
        await bot.send(message)


def merge_markup(primary: MessageMarkup, additional: MessageMarkup) -> MessageMarkup:
    return MessageMarkup(
        bubbles=(primary.bubbles + additional.bubbles),
        keyboard=(primary.keyboard + additional.keyboard),
    )
