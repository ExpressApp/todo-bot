"""Handlers for task list route."""

from botx import Bot, Collector, Message

from app.bot.commands.listing import CommandsEnum
from app.bot.dependencies.domain_repo import (
    get_task_from_message_dependency,
    task_attachment_repo_dependency,
    task_repo_dependency,
)
from app.db.tasks.repo.task import TaskRepo
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import Task
from app.services.answers import task_list
from app.services.pagination.pagination import pagination

collector = Collector()


@collector.handler(**CommandsEnum.TASK_LIST)
async def task_list_handler(
    message: Message, bot: Bot, task_repo: TaskRepo = task_repo_dependency
) -> None:
    tasks = await task_repo.get_all_tasks()

    tasks_descriptions = []
    if tasks:
        for task in tasks:
            task_description = task_list.get_task_message(message, task)
            tasks_descriptions.append(
                (
                    task_description.text,
                    task_description.markup,
                    task_description.options,
                )
            )

        await pagination(
            message,
            bot,
            tasks_descriptions,
            command=CommandsEnum.TASK_LIST.command,
            paginate_by=2,
        )
    else:
        await bot.send(task_list.get_empty_task_list_message(message))


@collector.hidden(**CommandsEnum.EXPAND_TASK)
async def expand_task_handler(
    message: Message,
    bot: Bot,
    task: Task = get_task_from_message_dependency,
    attachment_repo: TaskAttachmentRepo = task_attachment_repo_dependency,
) -> None:
    attachment_id = task.attachment_id
    markup = task_list.get_full_task_description_markup(message, task)

    if attachment_id:
        attachment = await attachment_repo.get_attachment_by_id(attachment_id)
        await bot.send(task_list.get_full_task_description_message(message, task))
        await bot.send(
            task_list.get_attachment_with_markup_message(message, attachment, markup)
        )
    else:
        await bot.send(
            task_list.get_full_task_description_message(message, task, markup)
        )


@collector.handler(**CommandsEnum.COMMANDS_HELP)
async def commands_help_handler(message: Message, bot: Bot) -> None:
    await bot.send(task_list.get_commands_help_message(message))
