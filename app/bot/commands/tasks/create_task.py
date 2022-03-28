from enum import Enum, auto
from pathlib import Path

from botx import Bot, HandlerCollector, IncomingMessage
from botx_fsm import FSMCollector

from app.bot import constants
from app.bot.middlewares.cancel_creation import cancel_creation_middleware
from app.bot.middlewares.db_session import db_session_middleware
from app.db.attachment.repo import AttachmentRepo
from app.db.task.repo import TaskRepo
from app.resources import strings
from app.schemas.enums import StrEnum
from app.services.answers.approve import get_task_approve_message
from app.services.answers.creation_status import get_status_message
from app.services.buttons.cancel import cancel_keyboard_button
from app.services.buttons.skip import skip_button
from app.services.file_storage import FileStorage


class CreateTaskStates(Enum):
    WAITING_TASK_TITLE = auto()
    WAITING_TASK_TEXT = auto()
    WAITING_TASK_CONTACT = auto()
    WAITING_TASK_ATTACHMENT = auto()
    WAITING_TASK_APPROVE = auto()


class TaskApproveCommands(StrEnum):
    YES = "YES"
    NO = "NO"


collector = HandlerCollector()
file_storage = FileStorage(Path(constants.FILE_STORAGE_PATH))
fsm = FSMCollector(CreateTaskStates)


@fsm.on(
    CreateTaskStates.WAITING_TASK_TITLE, 
    middlewares=[cancel_creation_middleware]
)
async def waiting_task_title_handler(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_TEXT,
        title=message.body,
    )
    await bot.answer_message(
        body="Введите текст задачи:",
        keyboard=cancel_keyboard_button()
    )


@fsm.on(
    CreateTaskStates.WAITING_TASK_TEXT,
    middlewares=[cancel_creation_middleware]
)
async def waiting_task_text_handler(message: IncomingMessage, bot: Bot) -> None:
    title = message.state.fsm_storage.title
    text = message.body
    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_CONTACT,
        title=title,
        text=text
    )

    await bot.answer_message(
        body="При необходимости отметьте **одного коллегу**, связанного с задачей, через `@@`:",
        bubbles=skip_button(),
        keyboard=cancel_keyboard_button()
    )


@fsm.on(
    CreateTaskStates.WAITING_TASK_CONTACT,
    middlewares=[cancel_creation_middleware]
)
async def waiting_task_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    title = message.state.fsm_storage.title
    text = message.state.fsm_storage.text

    if message.body == strings.SKIP_COMMAND:
        contact = None
    else:
        contact = message.mentions.contacts[0]

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_ATTACHMENT,
        title=title,
        text=text,
        contact=contact
    )

    await bot.answer_message(
        body="Прикрепите **вложение** (опционально):",
        bubbles=skip_button(),
        keyboard=cancel_keyboard_button()
    )


@fsm.on(
    CreateTaskStates.WAITING_TASK_ATTACHMENT,
    middlewares=[cancel_creation_middleware]
)
async def waiting_task_attachment_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.body == strings.СANCEL_COMMAND:
        await message.state.fsm.drop_state()
        await bot.send(message=get_status_message(message, strings.CANCEL_TITLE))
        return

    title = message.state.fsm_storage.title
    text = message.state.fsm_storage.text
    contact = message.state.fsm_storage.contact

    if message.body == strings.SKIP_COMMAND:
        file_storage_id = None
        filename = None
    else:
        async with message.file.open() as file:
            file_storage_id = await file_storage.save(file)
            filename = message.file.filename

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_APPROVE,
        title=title,
        text=text,
        contact=contact,
        file_storage_id=file_storage_id,
        filename=filename
    )

    await bot.send(
        message=get_task_approve_message(message, title, text, contact, filename, TaskApproveCommands)
    )


@fsm.on(
    CreateTaskStates.WAITING_TASK_APPROVE, 
    middlewares=[db_session_middleware, cancel_creation_middleware]
)
async def waiting_task_approve_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.body == strings.СANCEL_COMMAND:
        await message.state.fsm.drop_state()
        await bot.send(message=get_status_message(message, strings.CANCEL_TITLE))
        return

    title = message.state.fsm_storage.title
    text = message.state.fsm_storage.text
    contact = message.state.fsm_storage.contact
    file_storage_id = message.state.fsm_storage.file_storage_id
    filename = message.state.fsm_storage.filename

    db_session = message.state.db_session

    if message.body == TaskApproveCommands.YES:
        attachment_repo = AttachmentRepo(db_session)
        task_repo = TaskRepo(db_session)

        attachment_id = (await attachment_repo.create_attachment(file_storage_id, filename)).id
        await task_repo.create_task(
            message.sender.huid,
            title,
            text,
            contact.entity_id,
            attachment_id
        )
        await db_session.commit()

        await message.state.fsm.drop_state()
        await bot.send(message=get_status_message(message, strings.SUCCESS_TITLE))
    elif message.body == TaskApproveCommands.NO:
        await message.state.fsm.change_state(CreateTaskStates.WAITING_TASK_TITLE)
        await bot.answer_message(
            body="Введите название задачи:", 
            keyboard=cancel_keyboard_button()
        )
    else:
        await bot.send(
            message=get_task_approve_message(message, title, text, contact, filename)
        )


@collector.command("/создать", description="Создать новую задачу")
async def create_task_handler(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(CreateTaskStates.WAITING_TASK_TITLE)
    await bot.answer_message(
        body="Введите название задачи:", 
        keyboard=cancel_keyboard_button()
    )
    