"""Middleware for checking if a user pass a file or not."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc

from app.resources.strings import SKIP_COMMAND, WITHOUT_FILE
from app.services.buttons.cancel import get_cancel_keyboard_button
from app.services.buttons.skip import get_skip_button


async def file_checking_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    if message.body != SKIP_COMMAND:
        if not message.file:
            await bot.answer_message(
                body=WITHOUT_FILE,
                bubbles=get_skip_button(),
                keyboard=get_cancel_keyboard_button(),
            )
            return

    await call_next(message, bot)
