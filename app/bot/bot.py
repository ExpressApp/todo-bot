"""Configuration for bot instance."""
from botx import Bot, Depends
from botx_fsm import FSMMiddleware
from botx_fsm.storages.redis import RedisStorage
from loguru import logger

from app.bot.commands import common
from app.bot.commands.user import create_task, edit_task, task_list
from app.bot.dependencies.crud import auto_models_update
from app.bot.dependencies.errors import internal_error_handler
from app.bot.dependencies.external_cts import message_from_current_cts
from app.resources import strings
from app.settings.config import get_app_settings

config = get_app_settings()

redis_storage = RedisStorage(redis_dsn=str(config.REDIS_DSN), prefix="to-do-bot")
logger.debug(redis_storage.redis_dsn)
bot = Bot(
    bot_accounts=config.BOT_CREDENTIALS,
    dependencies=[Depends(message_from_current_cts), Depends(auto_models_update)],
)

bot.add_middleware(
    FSMMiddleware,
    storage=redis_storage,
    fsm_instances=[create_task.fsm, edit_task.fsm],
)

bot.startup_events = [redis_storage.init]
bot.shutdown_events = [redis_storage.close]

bot.state.bot_name = strings.BOT_NAME

bot.include_collector(common.collector)
bot.include_collector(create_task.collector)
bot.include_collector(task_list.collector)
bot.include_collector(edit_task.collector)

bot.add_exception_handler(Exception, internal_error_handler)
