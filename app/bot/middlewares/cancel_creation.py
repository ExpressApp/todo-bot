"""Middleware for checking if a user wants to cancel task creation"""

from typing import Callable

from botx import Bot, IncomingMessage, IncomingMessageHandlerFunc, OutgoingMessage

from app.resources.strings import CANCEL_COMMAND, CANCEL_TITLE
from app.services.answers.creation_status import get_status_message


async def cancel_creation_middleware(
    message: IncomingMessage, 
    bot: Bot, 
    call_next: IncomingMessageHandlerFunc
) -> None:
    if message.body == CANCEL_COMMAND:
        await message.state.fsm.drop_state()
        await bot.send(message=get_status_message(message, CANCEL_TITLE))
        return

    await call_next(message, bot)