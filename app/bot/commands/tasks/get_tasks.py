"""Handler for getting a task."""

from enum import Enum, auto
from math import ceil
from pathlib import Path
from typing import List
from uuid import UUID

from pybotx import (
    Bot,
    BubbleMarkup,
    Button,
    EditMessage,
    HandlerCollector,
    IncomingMessage,
    MentionBuilder,
    OutgoingAttachment,
    OutgoingMessage,
)
from pybotx_fsm import FSMCollector
from pydantic import parse_obj_as

from app.bot import constants
from app.bot.middlewares.db_session import db_session_middleware
from app.db.task.repo import TaskRepo
from app.resources import strings
from app.schemas.tasks import Task
from app.services.file_storage import FileStorage


class ChangeTaskDecriptionState(Enum):
    WAITING_NEW_DESCRIPTION = auto()


def build_main_task_messages(
    message: IncomingMessage,
    task: Task,
    has_attachment: bool,
) -> OutgoingMessage:
    colleague_id = task.mentioned_colleague_id
    contact = MentionBuilder.contact(colleague_id) if colleague_id else "Без контакта"

    message = OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=f"**{task.title}**\n\n{task.description}\n\n**Контакт:** {contact}",
    )

    if not has_attachment:
        message.bubbles = build_task_control_bubbles(task.id)

    return message


def build_file_attachment_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Подождите, файл отправляется...",
        bubbles=build_task_control_bubbles(message.data["task_id"]),
    )


def build_file_update_message(
    message: OutgoingMessage, sync_id: UUID, outgoing_attachment: OutgoingAttachment
) -> EditMessage:
    return EditMessage(
        bot_id=message.bot_id, sync_id=sync_id, body="", file=outgoing_attachment
    )


def build_task_control_bubbles(task_id: int) -> BubbleMarkup:
    bubbles = BubbleMarkup()
    bubbles.add_button(
        "/изменить",
        "Изменить описание",
        {"task_id": task_id},
    )
    bubbles.add_button(
        "/delete-task",
        "Удалить",
        {"task_id": task_id},
    )
    bubbles.add_button(
        "/список",
        "К списку задач",
    )

    return bubbles


def build_success_message(message: IncomingMessage) -> OutgoingMessage:
    bubbles = BubbleMarkup()
    bubbles.add_button(command="/список", label="Вернуться к списку задач")
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Описание задачи изменено.",
        bubbles=bubbles,
    )


collector = HandlerCollector()
fsm = FSMCollector(ChangeTaskDecriptionState)
file_storage = FileStorage(Path(constants.FILE_STORAGE_PATH))


class ListTasksWidget:
    def __init__(self, message: IncomingMessage):
        self.is_updating = "tasks" in message.metadata

        self._sync_ids = parse_obj_as(List[UUID], message.metadata.get("sync_ids", []))
        self._message = message
        self._tasks = parse_obj_as(List[Task], message.metadata.get("tasks", []))

        self._current_task_index = message.data.get("current_task_index", 0)
        self._current_page = message.data.get("current_page", 0)

    def set_tasks(self, tasks: List[Task]) -> None:  # noqa: WPS615
        self._tasks = tasks

    async def send(self, bot: Bot) -> None:
        assert self._tasks, "You must fetch tasks first."

        if self.is_updating:
            await self._update_message(bot)
        else:
            await self._send_message(bot)

    async def _update_message(self, bot: Bot) -> None:
        sync_ids = self._sync_ids + [self._message.source_sync_id]

        *messages, last_message = self._get_messages()
        last_message = self._prepare_last_message(last_message, sync_ids)

        edit_messages = [
            self._outgoing_to_edit_message(message, sync_id)
            for message, sync_id in zip(messages + [last_message], sync_ids)
        ]

        for message in edit_messages:
            await bot.edit(message=message)

    async def _send_message(self, bot: Bot) -> None:
        *messages, last_message = self._get_messages()

        sync_ids = [await bot.send(message=message) for message in messages]
        last_message = self._prepare_last_message(last_message, sync_ids)

        await bot.send(message=last_message)

    def _get_messages(self) -> List[OutgoingMessage]:
        messages = []

        for idx in range(  # noqa: WPS352
            self._current_task_index,
            self._current_task_index + constants.TASKS_LIST_PAGE_SIZE,
        ):
            message = self._get_task_message(idx)
            messages.append(message)

        return messages

    def _prepare_last_message(
        self, last_message: OutgoingMessage, sync_ids: List[UUID]
    ) -> OutgoingMessage:
        if last_message.bubbles:
            last_message.bubbles.add_row(self._get_control_buttons())
        else:
            bubbles = BubbleMarkup()
            bubbles.add_row(self._get_control_buttons())
            last_message.bubbles = bubbles
        last_message.metadata = {"tasks": self._tasks, "sync_ids": sync_ids}

        return last_message

    def _get_control_buttons(self) -> List[Button]:
        buttons = []

        if self._current_page > 0:
            buttons.append(
                Button(
                    command="/список",
                    label=(
                        strings.PREV_PAGE_LABEL_TEMPLATE.format(
                            cur_task_index=self._current_task_index
                        )
                    ),
                    data={
                        "current_task_index": (
                            self._current_task_index - constants.TASKS_LIST_PAGE_SIZE
                        ),
                        "current_page": self._current_page - 1,
                    },
                )
            )

        if self._can_add_page():
            buttons.append(
                Button(
                    command="/список",
                    label=(
                        strings.NEXT_PAGE_LABEL_TEMPLATE.format(
                            cur_task_index=self._current_task_index
                        )
                    ),
                    data={
                        "current_task_index": (
                            self._current_task_index + constants.TASKS_LIST_PAGE_SIZE
                        ),
                        "current_page": self._current_page + 1,
                    },
                )
            )

        return buttons

    def _get_task_message(self, idx: int) -> OutgoingMessage:
        if idx > len(self._tasks) - 1:
            return OutgoingMessage(
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                body="У вас больше нет задач",
            )

        task = self._tasks[idx]

        bubbles = BubbleMarkup()
        bubbles.add_button(
            command="/expand-task",
            label="Раскрыть задачу полностью",
            data={
                "task_id": task.id,
                "tasks": self._tasks,
                "current_task_index": idx,
            },
        )

        if len(task.description) > constants.MAX_PREVIEW_TEXT_LEN:
            task_text = task.description[: constants.MAX_PREVIEW_TEXT_LEN]
        else:
            task_text = task.description

        colleague_id = task.mentioned_colleague_id
        contact = (
            MentionBuilder.contact(colleague_id) if colleague_id else "Без контакта"
        )

        return OutgoingMessage(
            bot_id=self._message.bot.id,
            chat_id=self._message.chat.id,
            body=f"**{task.title}**\n\n{task_text}\n\n**Контакт:** {contact}",
            bubbles=bubbles,
        )

    def _outgoing_to_edit_message(
        self,
        outgoing_message: OutgoingMessage,
        sync_id: UUID,
    ) -> EditMessage:
        return EditMessage(
            bot_id=outgoing_message.bot_id,
            body=outgoing_message.body,
            bubbles=outgoing_message.bubbles,
            metadata=outgoing_message.metadata,
            sync_id=sync_id,
        )

    def _can_add_page(self) -> bool:
        return (
            self._current_page
            < ceil(len(self._tasks) / constants.TASKS_LIST_PAGE_SIZE) - 1  # noqa: W503
        )


@collector.command(
    "/список",
    description="Посмотреть список задач",
    middlewares=[db_session_middleware],
)
async def get_tasks(message: IncomingMessage, bot: Bot) -> None:  # noqa: WPS463
    widget = ListTasksWidget(message)

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
