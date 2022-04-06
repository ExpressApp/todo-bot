from pathlib import Path

from botx import Bot, BubbleMarkup, HandlerCollector, IncomingMessage

from app.bot import constants
from app.bot.middlewares.db_session import db_session_middleware
from app.interactors.delete_task import DeleteTaskInteractor
from app.services.answers.status import get_status_message
from app.services.file_storage import FileStorage

collector = HandlerCollector()
file_storage = FileStorage(Path(constants.FILE_STORAGE_PATH))


@collector.command(
    "/delete-task",
    visible=False,
    middlewares=[db_session_middleware],
)
async def delete_task(message: IncomingMessage, bot: Bot) -> None:
    assert message.source_sync_id

    interactor = DeleteTaskInteractor(
        db_session=message.state.db_session, file_storage=file_storage
    )

    await interactor.execute(message.data["task_id"])

    await bot.edit_message(
        bot_id=message.bot.id,
        sync_id=message.source_sync_id,
        body=f"**Задача успешно удалена.**",
        bubbles=BubbleMarkup(),
    )

    await bot.send(message=get_status_message(message))
