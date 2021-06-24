"""Dependencies with repos for domains models."""
from typing import Optional

from botx import Bot, DependencyFailure, Depends, Message
from botx_fsm import FlowError, StateExtractor

from app.bot.commands.listing import FSMCommandsEnum
from app.db.tasks.repo.task import TaskRepo
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import Task, TaskInCreation
from app.services.answers import creating_task, editing_task
from app.services.file_storage import file_storage

task_id_dependency = Depends(StateExtractor.task_id)


async def get_task_attachment_repo() -> TaskAttachmentRepo:
    return TaskAttachmentRepo(file_storage)


task_attachment_repo_dependency = Depends(get_task_attachment_repo)


async def get_task_repo(
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
) -> TaskRepo:
    return TaskRepo(attachment_repo)


task_repo_dependency = Depends(get_task_repo)

task_in_creation_dependency = Depends(StateExtractor.task)
forward_data_dependency = Depends(StateExtractor.forward_data)


async def handle_task_creating_cancelling(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
) -> None:
    if message.body == FSMCommandsEnum.CANCEL_PROCESS:
        await bot.send(creating_task.get_cancel_task_creation_message(message))
        if task.attachment:
            await attachment_repo.remove_attachment(task.attachment)
        raise FlowError(clear=True)


task_creating_cancelling_dependency = Depends(handle_task_creating_cancelling)


async def handle_task_editing_cancelling(
    message: Message,
    bot: Bot,
) -> None:
    if message.body == FSMCommandsEnum.CANCEL_PROCESS:
        await bot.send(editing_task.get_cancel_edit_task_message(message))
        raise FlowError(clear=True)


task_editing_cancelling_dependency = Depends(handle_task_editing_cancelling)


async def get_task_from_state(
    message: Message,
    bot: Bot,
    task_id: int = task_id_dependency,
    task_repo: TaskRepo = task_repo_dependency,
) -> Task:
    task = await task_repo.get_task_by_id(task_id)
    if not task:
        await bot.send(editing_task.task_not_exist_message(message))
        raise FlowError(clear=True)

    return task


get_task_from_state_dependency = Depends(get_task_from_state)


async def get_task_from_message(
    message: Message,
    bot: Bot,
    task_repo: TaskRepo = task_repo_dependency,
) -> Optional[Task]:
    try:
        task_id = message.command.data["task_id"]
    except KeyError:
        await bot.send(editing_task.get_must_push_button_for_editing_message(message))
        raise DependencyFailure

    task = await task_repo.get_task_by_id(task_id)
    if not task:
        await bot.send(editing_task.task_not_exist_message(message))
        raise DependencyFailure

    return task


get_task_from_message_dependency = Depends(get_task_from_message)
