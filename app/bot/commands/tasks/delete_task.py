from botx import Bot, BubbleMarkup, HandlerCollector, IncomingMessage

from app.bot.middlewares.db_session import db_session_middleware
from app.db.task.repo import TaskRepo
from app.resources import strings

collector = HandlerCollector()


@collector.command(
    "/delete-task",
    visible=False,
    middlewares=[db_session_middleware],
)
async def delete_task(message: IncomingMessage, bot: Bot) -> None:
    assert message.source_sync_id

    task_repo = TaskRepo(message.state.db_session)
    task_id = message.data["task_id"]

    task = await task_repo.get_task(task_id)
    await task_repo.delete_task(task_id)

    await bot.edit_message(
        bot_id=message.bot.id,
        sync_id=message.source_sync_id,
        body=strings.TASK_DELETED_TEMPLATE.format(task=task),
        bubbles=BubbleMarkup(),
    )
