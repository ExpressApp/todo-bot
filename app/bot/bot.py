"""Configuration for bot instance."""

from botx import Bot
from pybotx_fsm import FSMMiddleware
from pybotx_smart_logger import BotXSmartLoggerMiddleware

from app.bot.commands import common
from app.bot.commands.tasks import create_task, delete_task, get_tasks
from app.bot.error_handlers.internal_error import internal_error_handler
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
            FSMMiddleware(
                [create_task.fsm, get_tasks.fsm], state_repo_key="redis_repo"
            ),
            BotXSmartLoggerMiddleware(debug_enabled_for_message=True).dispatch,
        ],
    )
