"""Handlers for default bot commands and system events."""

from os import environ

from botx import Bot, Collector, Message

from app.bot.commands.user.create_task import TaskCreationEnum, fsm
from app.resources import strings
from app.schemas.task import TaskInCreation
from app.services.answers.common import chat_created_message, default_message
from app.services.answers.task_from_forward import get_decision_create_task_message

collector = Collector()


@collector.default(include_in_status=False)
async def default_handler(message: Message, bot: Bot) -> None:
    """Run if command not found."""
    if message.is_forward:
        await bot.send(get_decision_create_task_message(message))
        await fsm.change_state(
            message,
            TaskCreationEnum.DECISION_CREATE_TASK,
            forward_data=message.command.body,
            task=TaskInCreation(title=""),
        )
    else:
        await bot.send(default_message(message))


@collector.chat_created
async def chat_created(message: Message, bot: Bot) -> None:
    """Send a welcome message and the bot functionality in new created chat."""
    await bot.send(chat_created_message(message))


@collector.handler(
    command="/help", name="help", description=strings.HELP_COMMAND_DESCRIPTION
)
async def show_help(message: Message, bot: Bot) -> None:
    """Справка по командам."""
    status = await message.bot.status()

    # For each public command:
    # * collect full description or
    # * collect short description like in status or
    # * skip command without any description
    commands = []
    for command in status.result.commands:
        command_handler = message.bot.handler_for(command.name)
        description = command_handler.full_description or command_handler.description
        if description:
            commands.append((command.body, description))

    text = strings.HELP_COMMAND_MESSAGE_TEMPLATE.format(commands=commands)
    await bot.answer_message(text, message)


@collector.hidden(command="/_debug:git-commit-sha")
async def git_commit_sha(message: Message, bot: Bot) -> None:
    """Show git commit SHA."""
    await bot.answer_message(environ.get("GIT_COMMIT_SHA", "<undefined>"), message)
