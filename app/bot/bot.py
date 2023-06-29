"""Configuration for bot instance."""

from pybotx import Bot
from pybotx_fsm import FSMMiddleware

from app.bot.commands import common
from app.bot.commands.tasks import create_task, delete_task, get_tasks
from app.bot.error_handlers.internal_error import internal_error_handler
from app.bot.middlewares.smart_logger import smart_logger_middleware
from app.settings import settings


def get_bot() -> Bot:
    return Bot(
        collectors=[
            common.collector,
            create_task.collector,
            delete_task.collector,
            get_tasks.collector,
        ],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers={Exception: internal_error_handler},
        middlewares=[
            smart_logger_middleware,
            FSMMiddleware(
                [create_task.fsm, get_tasks.fsm], state_repo_key="redis_repo"
            ),
        ],
    )
