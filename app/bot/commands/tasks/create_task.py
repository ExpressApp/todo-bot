from enum import Enum, auto

from botx import Bot, BubbleMarkup, HandlerCollector, IncomingMessage, OutgoingMessage
from botx_fsm import FSMCollector

from app.bot.middlewares.db_session import db_session_middleware
from app.db.task.repo import TaskRepo
from app.resources import strings
from app.schemas.enums import StrEnum

collector = HandlerCollector()


class CreateTaskStates(Enum):
    WAITING_TASK_TITLE = auto()
    WAITING_TASK_TEXT = auto()
    WAITING_TASK_APPROVE = auto()


class TaskApproveCommands(StrEnum):
    YES = "YES"
    NO = "NO"  # noqa: WPS110


def get_task_approve_message(
    message: IncomingMessage, title: str, text: str
) -> OutgoingMessage:
    bubbles = BubbleMarkup()
    bubbles.add_button(command=TaskApproveCommands.YES, label=strings.YES_LABEL)
    bubbles.add_button(command=TaskApproveCommands.NO, label=strings.NO_LABEL)

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.TASK_CREATED_TEMPLATE.format(title=title, text=text),
        bubbles=bubbles,
    )


fsm = FSMCollector(CreateTaskStates)


@fsm.on(CreateTaskStates.WAITING_TASK_TITLE)
async def waiting_task_title_handler(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_TEXT,
        title=message.body,
    )
    await bot.answer_message(strings.INPUT_TASK_TEXT_TEXT)


@fsm.on(CreateTaskStates.WAITING_TASK_TEXT)
async def waiting_task_text_handler(message: IncomingMessage, bot: Bot) -> None:
    title = message.state.fsm_storage.title
    text = message.body

    await message.state.fsm.change_state(
        CreateTaskStates.WAITING_TASK_APPROVE,
        title=title,
        text=text,
    )

    await bot.send(message=get_task_approve_message(message, title, text))


@fsm.on(CreateTaskStates.WAITING_TASK_APPROVE, middlewares=[db_session_middleware])
async def waiting_task_approve_handler(message: IncomingMessage, bot: Bot) -> None:
    title = message.state.fsm_storage.title
    text = message.state.fsm_storage.text

    if message.body == TaskApproveCommands.YES:
        task_repo = TaskRepo(message.state.db_session)
        await task_repo.create_task(message.sender.huid, title, text)

        await message.state.fsm.drop_state()
        await bot.answer_message(strings.TASK_CREATED_TEXT)
    elif message.body == TaskApproveCommands.NO:
        await message.state.fsm.change_state(CreateTaskStates.WAITING_TASK_TITLE)
        await bot.answer_message(strings.INPUT_TASK_TITLE_TEXT)
    else:
        await bot.send(message=get_task_approve_message(message, title, text))


@collector.command("/создать", description="Создать новую задачу")
async def create_task_handler(message: IncomingMessage, bot: Bot) -> None:
    await message.state.fsm.change_state(CreateTaskStates.WAITING_TASK_TITLE)

    await bot.answer_message(strings.INPUT_TASK_TITLE_TEXT)
