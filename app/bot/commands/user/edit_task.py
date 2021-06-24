"""Handlers for edit task route."""

from enum import Enum, auto

from botx import Bot, Collector, Message
from botx_fsm import FSM, FlowError

from app.bot.commands.listing import CommandsEnum
from app.bot.commands.user.task_list import task_attachment_repo_dependency
from app.bot.dependencies.domain_repo import (
    get_task_from_message_dependency,
    get_task_from_state_dependency,
    task_editing_cancelling_dependency,
    task_repo_dependency,
)
from app.db.tasks.repo.task import TaskRepo
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import Task
from app.services.answers import creating_task, editing_task


class TaskEditEnum(Enum):
    EDIT_TITLE = auto()
    EDIT_DESCRIPTION = auto()
    ADD_MENTION = auto()
    ADD_ATTACHMENT = auto()


collector = Collector()
fsm = FSM(TaskEditEnum, dependencies=[task_editing_cancelling_dependency])


@fsm.on(TaskEditEnum.EDIT_TITLE)
async def wait_edit_title(
    message: Message,
    bot: Bot,
    task: Task = get_task_from_state_dependency,
    task_repo: TaskRepo = task_repo_dependency,
) -> None:
    new_title = message.body
    if new_title:
        task.title = new_title
        await task_repo.edit_task(task)
        await bot.send(editing_task.get_successful_edit_title_message(message))
        await bot.send(editing_task.get_edit_task_message(message, task))
        raise FlowError(clear=True)

    await bot.send(creating_task.get_file_when_title_required_message(message))


@fsm.on(TaskEditEnum.EDIT_DESCRIPTION)
async def wait_edit_description(
    message: Message,
    bot: Bot,
    task: Task = get_task_from_state_dependency,
    task_repo: TaskRepo = task_repo_dependency,
) -> None:
    new_description = message.body
    if new_description:
        task.description = new_description
        await task_repo.edit_task(task)
        await bot.send(editing_task.get_successful_edit_description_message(message))
        await bot.send(editing_task.get_edit_task_message(message, task))
        raise FlowError(clear=True)

    await bot.send(creating_task.get_file_when_description_required_message(message))


@fsm.on(TaskEditEnum.ADD_MENTION)
async def wait_edit_mention(
    message: Message,
    bot: Bot,
    task: Task = get_task_from_state_dependency,
    task_repo: TaskRepo = task_repo_dependency,
) -> None:
    try:
        mentions = message.entities.mentions[0]
    except IndexError:
        await bot.send(creating_task.get_mention_validation_message(message))
        return

    assignee = mentions.mention_data.user_huid
    task.assignee = assignee
    await task_repo.edit_task(task)

    await bot.send(editing_task.get_successful_add_mention_message(message))
    await bot.send(editing_task.get_edit_task_message(message, task))

    raise FlowError(clear=True)


@fsm.on(TaskEditEnum.ADD_ATTACHMENT)
async def wait_edit_attachment(
    message: Message,
    bot: Bot,
    task: Task = get_task_from_state_dependency,
    task_repo: TaskRepo = task_repo_dependency,
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
) -> None:
    try:
        attachment = message.attachments.file
    except AttributeError:
        await bot.send(creating_task.get_text_when_file_required_message(message))
        return

    try:
        attachment = await attachment_repo.create_attachment(attachment)
    except ValueError:
        await bot.send(creating_task.get_attachment_not_support_message(message))
        return

    task.attachment_id = attachment.id
    await task_repo.edit_task(task)

    await bot.send(editing_task.get_successful_add_attachment_message(message))
    await bot.send(editing_task.get_edit_task_message(message, task))

    raise FlowError(clear=True)


@collector.hidden(**CommandsEnum.EDIT_TASK)
async def edit_information_handler(
    message: Message, bot: Bot, task: Task = get_task_from_message_dependency
) -> None:
    await bot.send(editing_task.get_edit_task_message(message, task))


@collector.hidden(**CommandsEnum.EDIT_TITLE)
async def edit_title_handler(
    message: Message, bot: Bot, task: Task = get_task_from_message_dependency
) -> None:
    await bot.send(editing_task.get_edit_title_message(message))
    await fsm.change_state(message, TaskEditEnum.EDIT_TITLE, task_id=task.id)


@collector.hidden(**CommandsEnum.EDIT_DESCRIPTION)
async def edit_description_handler(
    message: Message, bot: Bot, task: Task = get_task_from_message_dependency
) -> None:
    await bot.send(editing_task.get_edit_description_message(message))
    await fsm.change_state(message, TaskEditEnum.EDIT_DESCRIPTION, task_id=task.id)


@collector.hidden(**CommandsEnum.EDIT_MENTION)
async def edit_mention_handler(
    message: Message,
    bot: Bot,
    task_repo: TaskRepo = task_repo_dependency,
    task: Task = get_task_from_message_dependency,
) -> None:
    if task.assignee is None:
        await bot.send(editing_task.get_add_mention_message(message))
        await fsm.change_state(message, TaskEditEnum.ADD_MENTION, task_id=task.id)
    else:
        task.assignee = None
        await task_repo.edit_task(task)
        await bot.send(editing_task.get_successful_delete_mention_message(message))
        await bot.send(editing_task.get_edit_task_message(message, task))


@collector.hidden(**CommandsEnum.EDIT_ATTACHMENT)
async def edit_attachment_handler(
    message: Message,
    bot: Bot,
    task_repo: TaskRepo = task_repo_dependency,
    task: Task = get_task_from_message_dependency,
) -> None:
    if task.attachment_id is None:
        await bot.send(editing_task.get_add_attachment_message(message))
        await fsm.change_state(message, TaskEditEnum.ADD_ATTACHMENT, task_id=task.id)
    else:
        task.attachment_id = None
        await task_repo.edit_task(task)
        await bot.send(editing_task.get_successful_delete_attachment_message(message))
        await bot.send(editing_task.get_edit_task_message(message, task))


@collector.hidden(**CommandsEnum.DELETE_TASK)
async def delete_task_handler(
    message: Message,
    bot: Bot,
    task_repo: TaskRepo = task_repo_dependency,
    task: Task = get_task_from_message_dependency,
) -> None:
    await task_repo.delete_task(task_id=task.id, attachment_id=task.attachment_id)
    await bot.send(editing_task.get_delete_task_message(message))
