"""Handler for task creation."""

from enum import Enum, auto
from pathlib import Path

from pybotx import Bot, HandlerCollector, IncomingMessage
from pybotx_fsm import FSMCollector

from app.bot import constants
from app.bot.middlewares.cancel_creation import cancel_creation_middleware
from app.bot.middlewares.db_session import db_session_middleware
from app.bot.middlewares.file_checking import file_checking_middleware
from app.interactors.create_task import CreateTaskInteractor
from app.resources import strings
from app.schemas.attachments import AttachmentInCreation
from app.schemas.tasks import TaskInCreation
from app.services.answers.approve import get_task_approve_message
from app.services.answers.status import get_status_message
from app.services.buttons.cancel import get_cancel_keyboard_button
from app.services.buttons.skip import get_skip_button
from app.services.file_storage import FileStorage


class CreateTaskStates(Enum):
    WAITING_TASK_TITLE = auto()
    WAITING_TASK_TEXT = auto()
    WAITING_TASK_CONTACT = auto()
    WAITING_TASK_ATTACHMENT = auto()
    WAITING_TASK_APPROVE = auto()


collector = HandlerCollector()
file_storage = FileStorage(Path(constants.FILE_STORAGE_PATH))
fsm = FSMCollector(CreateTaskStates)


@fsm.on(CreateTaskStates.WAITING_TASK_TITLE, middlewares=[cancel_creation_middleware])
async def waiting_task_title_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.file:
        await bot.answer_message(
            body=strings.FILE_NOT_TITLE, keyboard=get_cancel_keyboard_button()
        )
        return

    task = message.state.fsm_storage.task
    task.title = message.body

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_TEXT,
        task=task,
    )
    await bot.answer_message(
        body="Введите текст задачи:", keyboard=get_cancel_keyboard_button()
    )


@fsm.on(CreateTaskStates.WAITING_TASK_TEXT, middlewares=[cancel_creation_middleware])
async def waiting_task_text_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.file:
        await bot.answer_message(
            body=strings.FILE_NOT_DESCRIPTION, keyboard=get_cancel_keyboard_button()
        )
        return

    task = message.state.fsm_storage.task
    task.description = message.body

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_CONTACT, task=task
    )

    await bot.answer_message(
        body=strings.ASK_CONTACT,
        bubbles=get_skip_button(),
        keyboard=get_cancel_keyboard_button(),
    )


@fsm.on(CreateTaskStates.WAITING_TASK_CONTACT, middlewares=[cancel_creation_middleware])
async def waiting_task_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    task = message.state.fsm_storage.task

    if message.body != strings.SKIP_COMMAND:
        if len(message.mentions.contacts) != 1:
            await bot.answer_message(
                body=strings.INCORRECT_CONTACT,
                bubbles=get_skip_button(),
                keyboard=get_cancel_keyboard_button(),
            )
            return

        task.mentioned_colleague_id = message.mentions.contacts[0].entity_id

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_ATTACHMENT, task=task
    )

    await bot.answer_message(
        body="Прикрепите **вложение** (опционально):",
        bubbles=get_skip_button(),
        keyboard=get_cancel_keyboard_button(),
    )


@fsm.on(
    CreateTaskStates.WAITING_TASK_ATTACHMENT,
    middlewares=[cancel_creation_middleware, file_checking_middleware],
)
async def waiting_task_attachment_handler(message: IncomingMessage, bot: Bot) -> None:
    task = message.state.fsm_storage.task
    attachment = AttachmentInCreation()

    if message.body != strings.SKIP_COMMAND:
        async with message.file.open() as file:
            file_storage_id = await file_storage.save(file)
            filename = message.file.filename

            attachment.file_storage_id = file_storage_id
            attachment.filename = filename

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_APPROVE, task=task, attachment=attachment
    )

    await bot.answer_message(strings.BEFORE_APPROVE)
    await bot.send(message=get_task_approve_message(message, task, attachment))


@fsm.on(
    CreateTaskStates.WAITING_TASK_APPROVE,
    middlewares=[db_session_middleware, cancel_creation_middleware],
)
async def waiting_task_approve_handler(message: IncomingMessage, bot: Bot) -> None:
    task = message.state.fsm_storage.task
    attachment = message.state.fsm_storage.attachment

    db_session = message.state.db_session

    if message.body == strings.CONFIRM_TASK_COMMAND:
        interactor = CreateTaskInteractor(db_session)
        task = await interactor.execute(task, attachment)

        await message.state.fsm.drop_state()
        await bot.send(message=get_status_message(message, strings.SUCCESS_TITLE))

    elif message.body == strings.CANCEL_TASK_COMMAND:
        await message.state.fsm.change_state(CreateTaskStates.WAITING_TASK_TITLE)
        if attachment.file_storage_id:
            await file_storage.remove(attachment.file_storage_id)
        await bot.answer_message(
            body=strings.INPUT_TASK_TITLE, keyboard=get_cancel_keyboard_button()
        )

    else:
        await bot.send(message=get_task_approve_message(message, task, attachment))


@collector.command("/создать", description="Создать новую задачу")
async def create_task_handler(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_TITLE,
        task=TaskInCreation(user_huid=message.sender.huid),
    )
    await bot.answer_message(
        body=strings.INPUT_TASK_TITLE, keyboard=get_cancel_keyboard_button()
    )
