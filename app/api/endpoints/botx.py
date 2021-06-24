"""Endpoints for communication with botx."""

from botx import IncomingMessage, Status
from fastapi import APIRouter
from starlette.status import HTTP_202_ACCEPTED

from app.bot.bot import bot

router = APIRouter()


@router.post("/command", name="botx:command", status_code=HTTP_202_ACCEPTED)
async def bot_command(message: IncomingMessage) -> None:
    """Receive commands from users. Max timeout - 5 seconds."""

    await bot.execute_command(message.dict())


@router.get("/status", name="botx:status", response_model=Status)
async def bot_status() -> Status:
    """Send commands with short descriptions."""
    return await bot.status()
