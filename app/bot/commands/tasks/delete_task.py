from pathlib import Path

from botx import Bot, BubbleMarkup, HandlerCollector, IncomingMessage

from app.bot import constants
from app.bot.middlewares.db_session import db_session_middleware
from app.db.attachment.repo import AttachmentRepo
from app.db.task.repo import TaskRepo
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

    db_session = message.state.db_session

    attachment_repo = AttachmentRepo(db_session)
    task_repo = TaskRepo(message.state.db_session)

    task_id = message.data["task_id"]

    task = await task_repo.get_task(task_id)
    await task_repo.delete_task(task_id)

    if task.attachment_id:
        attachment = await attachment_repo.get_attachment(task.attachment_id)
        await attachment_repo.remove_attachment(attachment.id)
        await file_storage.remove(attachment.file_storage_id)
    
    await db_session.commit()

    await bot.edit_message(
        bot_id=message.bot.id,
        sync_id=message.source_sync_id,
        body=f"**Задача успешно удалена.**",
        bubbles=BubbleMarkup(),
    )

    await bot.send(message=get_status_message(message))
