"""Endpoints for communication with botx."""

from http import HTTPStatus

from botx import (
    Bot,
    BotXMethodCallbackNotFoundError,
    UnknownBotAccountError,
    build_bot_disabled_response,
    build_command_accepted_response,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.dependencies.bot import bot_dependency
from app.logger import logger
from app.settings import settings

router = APIRouter()


@router.post("/command")
async def command_handler(request: Request, bot: Bot = bot_dependency) -> JSONResponse:
    """Receive commands from users. Max timeout - 5 seconds."""

    try:
        bot.async_execute_raw_bot_command(await request.json())
    except ValueError:
        error_label = "Bot command validation error"

        if settings.DEBUG:
            logger.exception(error_label)
        else:
            logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    except UnknownBotAccountError as exc:
        error_label = f"No credentials for bot {exc.bot_id}"
        logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    return JSONResponse(
        build_command_accepted_response(), status_code=HTTPStatus.ACCEPTED
    )


@router.get("/status")
async def status_handler(request: Request, bot: Bot = bot_dependency) -> JSONResponse:
    """Show bot status and commands list."""

    try:
        status = await bot.raw_get_status(dict(request.query_params))
    except UnknownBotAccountError as exc:
        error_label = f"Unknown bot_id: {exc.bot_id}"
        logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    return JSONResponse(status)


@router.post("/notification/callback")
async def callback_handler(request: Request, bot: Bot = bot_dependency) -> JSONResponse:
    """Process BotX methods callbacks."""

    try:
        bot.set_raw_botx_method_result(await request.json())
    except BotXMethodCallbackNotFoundError as exc:
        error_label = f"Unexpected callback with sync_id: {exc.sync_id}"
        logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
