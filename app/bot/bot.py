"""Configuration for bot instance."""

from botx import Bot
from botx_fsm import FSMMiddleware

from app.bot.commands import common
from app.bot.commands.tasks import create_task
from app.bot.error_handlers.internal_error import internal_error_handler
from app.settings import settings


def get_bot() -> Bot:
    return Bot(
        collectors=[common.collector, create_task.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers={Exception: internal_error_handler},
        middlewares=[FSMMiddleware([create_task.fsm], state_repo_key="redis_repo")],
    )
