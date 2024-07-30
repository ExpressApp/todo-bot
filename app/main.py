"""Application with configuration for events, routers and middleware."""

from functools import partial

import aioredis
from fastapi import FastAPI
from pybotx import Bot

from app.api.routers import router
from app.bot.bot import get_bot
from app.caching.callback_redis_repo import CallbackRedisRepo
from app.caching.redis_repo import RedisRepo
from app.db.sqlalchemy import build_db_session_factory
from app.resources import strings
from app.settings import settings


async def startup(application: FastAPI) -> None:
    # -- Database --
    db_session_factory = await build_db_session_factory()

    # -- Redis --
    redis_repo = await RedisRepo.init(
        dsn=settings.REDIS_DSN, prefix=strings.BOT_PROJECT_NAME
    )
    redis_client = await aioredis.create_redis_pool(settings.REDIS_DSN)

    # -- Bot --
    callback_repo = CallbackRedisRepo(redis_client)
    bot = get_bot(callback_repo)

    await bot.startup()

    bot.state.db_session_factory = db_session_factory
    bot.state.redis_repo = redis_repo

    application.state.bot = bot
    application.state.redis = redis_client


async def shutdown(application: FastAPI) -> None:
    # -- Bot --
    bot: Bot = application.state.bot
    await bot.shutdown()

    # -- Redis --
    await bot.state.redis_repo.close()


def get_application() -> FastAPI:
    """Create configured server application instance."""
    application = FastAPI(title=strings.BOT_PROJECT_NAME)

    application.add_event_handler("startup", partial(startup, application))
    application.add_event_handler("shutdown", partial(shutdown, application))

    application.include_router(router)

    return application


app = get_application()
