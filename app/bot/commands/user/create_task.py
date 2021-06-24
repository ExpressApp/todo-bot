"""Handlers for create task route."""

from enum import Enum, auto

from botx import Bot, Collector, Message
from botx_fsm import FSM, FlowError

from app.bot.commands.listing import CommandsEnum, FSMCommandsEnum
from app.bot.dependencies.domain_repo import (
    forward_data_dependency,
    task_attachment_repo_dependency,
    task_creating_cancelling_dependency,
    task_in_creation_dependency,
    task_repo_dependency,
)
from app.db.tasks.repo.task import TaskRepo
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import TaskInCreation
from app.services.answers import creating_task, task_from_forward

collector = Collector()


class TaskCreationEnum(Enum):
    WAITING_TITLE = auto()
    WAITING_DESCRIPTION = auto()
    WAITING_MENTION = auto()
    WAITING_ATTACHMENT = auto()
    WAITING_CONFIRMATION = auto()
    DECISION_CREATE_TASK = auto()
    MESSAGE_AS_TITLE_OR_DESCRIPTION = auto()


fsm = FSM(TaskCreationEnum, dependencies=[task_creating_cancelling_dependency])


@fsm.on(
    TaskCreationEnum.WAITING_TITLE,
)
async def wait_input_title(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
) -> None:
    title = message.body
    if title:
        task.title = title
        # In case forward message
        if task.description:
            await bot.send(creating_task.get_input_mention_message(message))
            await fsm.change_state(message, TaskCreationEnum.WAITING_MENTION, task=task)
        else:
            await bot.send(creating_task.get_input_description_message(message))
            await fsm.change_state(
                message, TaskCreationEnum.WAITING_DESCRIPTION, task=task
            )
    else:
        await bot.send(creating_task.get_file_when_title_required_message(message))
        return


@fsm.on(
    TaskCreationEnum.WAITING_DESCRIPTION,
)
async def wait_input_description(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
) -> None:
    decision = message.body
    if decision:
        if decision != FSMCommandsEnum.SKIP_INPUT:
            task.description = message.body
        await bot.send(creating_task.get_input_mention_message(message))

        await fsm.change_state(message, TaskCreationEnum.WAITING_MENTION, task=task)
    else:
        await bot.send(
            creating_task.get_file_when_description_required_message(message)
        )
        return


@fsm.on(
    TaskCreationEnum.WAITING_MENTION,
)
async def wait_input_mention(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
) -> None:
    decision = message.body
    if decision != FSMCommandsEnum.SKIP_INPUT:
        try:
            mentions = message.entities.mentions[0]
        except (KeyError, IndexError):
            await bot.send(creating_task.get_mention_validation_message(message))
            return

        task.assignee = mentions.mention_data.user_huid

    await bot.send(creating_task.get_input_attachment_message(message))

    await fsm.change_state(message, TaskCreationEnum.WAITING_ATTACHMENT, task=task)


@fsm.on(
    TaskCreationEnum.WAITING_ATTACHMENT,
)
async def wait_upload_attachment(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
) -> None:
    decision = message.body
    if decision != FSMCommandsEnum.SKIP_INPUT:
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

        task.attachment = attachment.id

    await bot.send(creating_task.get_checking_data_message(message))
    await bot.send(creating_task.get_full_task_description_message(message, task))

    await fsm.change_state(message, TaskCreationEnum.WAITING_CONFIRMATION, task=task)


@fsm.on(
    TaskCreationEnum.WAITING_CONFIRMATION,
)
async def wait_confirmation(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
    task_repo: TaskRepo = task_repo_dependency,
) -> None:
    decision = message.body

    if decision == FSMCommandsEnum.YES:
        await task_repo.create_task(task)
        await bot.send(creating_task.get_success_creating_task_message(message))
        raise FlowError(clear=True)

    elif decision == FSMCommandsEnum.NO:
        if task.attachment:
            await attachment_repo.remove_attachment(task.attachment)
        await bot.send(creating_task.get_input_title_message(message))
        await fsm.change_state(
            message, TaskCreationEnum.WAITING_TITLE, task=TaskInCreation(title="")
        )
    else:
        await bot.send(creating_task.get_re_checking_data_message(message))
        await bot.send(creating_task.get_full_task_description_message(message, task))
        return


@fsm.on(
    TaskCreationEnum.DECISION_CREATE_TASK,
)
async def decision_create_task(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
    forward_data: str = forward_data_dependency,
) -> None:
    decision = message.body
    if decision == FSMCommandsEnum.NO:
        await bot.send(creating_task.get_cancel_task_creation_message(message))
        raise FlowError(clear=True)
    elif decision == FSMCommandsEnum.YES:
        await bot.send(task_from_forward.get_as_title_or_description_message(message))
        await fsm.change_state(
            message,
            TaskCreationEnum.MESSAGE_AS_TITLE_OR_DESCRIPTION,
            forward_data=forward_data,
            task=task,
        )
    else:
        await bot.send(
            task_from_forward.get_text_when_command_required_message(message)
        )
        await bot.send(task_from_forward.get_decision_create_task_message(message))
        return


@fsm.on(
    TaskCreationEnum.MESSAGE_AS_TITLE_OR_DESCRIPTION,
)
async def message_as_title_or_description(
    message: Message,
    bot: Bot,
    task: TaskInCreation = task_in_creation_dependency,
    forward_data: str = forward_data_dependency,
) -> None:
    decision = message.body
    if decision == FSMCommandsEnum.MESSAGE_AS_TITLE:
        task.title = forward_data
        await bot.send(creating_task.get_input_description_message(message))
        await fsm.change_state(
            message,
            TaskCreationEnum.WAITING_DESCRIPTION,
            task=task,
        )
    elif decision == FSMCommandsEnum.MESSAGE_AS_DESCRIPTION:
        task.description = forward_data
        await bot.send(creating_task.get_input_title_message(message))
        await fsm.change_state(
            message,
            TaskCreationEnum.WAITING_TITLE,
            task=task,
        )
    else:
        await bot.send(
            task_from_forward.get_text_when_command_required_message(message)
        )
        await bot.send(task_from_forward.get_as_title_or_description_message(message))
        return


@collector.handler(**CommandsEnum.CREATE_TASK)
async def create_task_handler(message: Message, bot: Bot) -> None:
    await bot.send(creating_task.get_input_title_message(message))
    await fsm.change_state(
        message, TaskCreationEnum.WAITING_TITLE, task=TaskInCreation(title="")
    )
