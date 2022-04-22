"""Handler for getting a task."""

from enum import Enum, auto
from pathlib import Path

from pybotx import Bot, HandlerCollector, IncomingMessage, OutgoingAttachment
from pybotx_fsm import FSMCollector

from app.bot import constants
from app.bot.answers.file_attachment import (
    build_file_attachment_message,
    build_file_update_message,
)
from app.bot.answers.main_task import build_main_task_messages
from app.bot.answers.success import build_success_message
from app.bot.middlewares.db_session import db_session_middleware
from app.bot.widgets.tasks_list import TasksListWidget
from app.db.task.repo import TaskRepo
from app.resources import strings
from app.services.file_storage import FileStorage


class ChangeTaskDecriptionState(Enum):
    WAITING_NEW_DESCRIPTION = auto()


collector = HandlerCollector()
fsm = FSMCollector(ChangeTaskDecriptionState)
file_storage = FileStorage(Path(constants.FILE_STORAGE_PATH))


@collector.command(
    "/список",
    description="Посмотреть список задач",
    middlewares=[db_session_middleware],
)
async def get_tasks(message: IncomingMessage, bot: Bot) -> None:  # noqa: WPS463
    widget = TasksListWidget(message)

    if not widget.is_updating:
        task_repo = TaskRepo(message.state.db_session)
        tasks = await task_repo.get_user_tasks(message.sender.huid)

        if not tasks:
            await bot.answer_message("У вас нет задач")
            return

        await bot.answer_message(body=strings.TASKS_NUM_TEMPLATE.format(num=len(tasks)))

        widget.set_tasks(tasks)

    await widget.send(bot)


@collector.command(
    "/expand-task",
    visible=False,
    middlewares=[db_session_middleware],
)
async def expand_task(message: IncomingMessage, bot: Bot) -> None:
    assert message.source_sync_id

    task_repo = TaskRepo(message.state.db_session)

    task = await task_repo.get_task(message.data["task_id"])

    await bot.send(
        message=build_main_task_messages(message, task, bool(task.attachment))
    )

    if task.attachment:
        outgoing_to_edit_message = build_file_attachment_message(message)
        sync_id = await bot.send(message=outgoing_to_edit_message)

        async with file_storage.file(task.attachment.file_storage_id) as file:
            outgoing_attachment = await OutgoingAttachment.from_async_buffer(
                file, task.attachment.filename
            )

        await bot.edit(
            message=build_file_update_message(
                outgoing_to_edit_message, sync_id, outgoing_attachment
            )
        )


@collector.command("/изменить", visible=False)
async def delete_task(message: IncomingMessage, bot: Bot) -> None:
    task_id = message.data["task_id"]

    await message.state.fsm.change_state(
        ChangeTaskDecriptionState.WAITING_NEW_DESCRIPTION, task_id=task_id
    )

    await bot.answer_message(body="Укажите новое описание задачи:")


@fsm.on(
    ChangeTaskDecriptionState.WAITING_NEW_DESCRIPTION,
    middlewares=[db_session_middleware],
)
async def waiting_new_description_handler(message: IncomingMessage, bot: Bot) -> None:
    new_description = message.body
    task_id = message.state.fsm_storage.task_id

    db_session = message.state.db_session
    task_repo = TaskRepo(db_session)

    await task_repo.change_task_description(task_id, new_description)
    await db_session.commit()

    await message.state.fsm.drop_state()
    await bot.send(message=build_success_message(message))
