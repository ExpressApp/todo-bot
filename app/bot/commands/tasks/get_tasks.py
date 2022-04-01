from pathlib import Path
from typing import List
from uuid import UUID

from botx import (
    Bot,
    BubbleMarkup,
    Button,
    EditMessage,
    HandlerCollector,
    IncomingMessage,
    Mention,
    OutgoingAttachment,
    OutgoingMessage,
)
from pydantic import parse_obj_as
from app.bot import constants

from app.bot.middlewares.db_session import db_session_middleware
from app.bot import constants
from app.db.attachment.repo import AttachmentRepo
from app.db.task.repo import TaskRepo
from app.schemas.tasks import Task
from app.services.file_storage import FileStorage

collector = HandlerCollector()

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
        *messages, last_message = self._get_messages()
        last_message = self._prepare_last_message(last_message)

        edit_messages = [
            self._outgoing_to_edit_message(message, sync_id)
            for message, sync_id in zip(
                messages + [last_message],
                self._sync_ids + [self._message.source_sync_id]
            )
        ]

        for message in edit_messages:
            await bot.edit(message=message)

    async def _send_message(self, bot: Bot) -> None:
        *messages, last_message = self._get_messages()

        self._sync_ids = [await bot.send(message=message) for message in messages]

        last_message = self._prepare_last_message(last_message)
        await bot.send(message=last_message)

    def _get_messages(self) -> List[OutgoingMessage]:
        messages = []

        for i in range(constants.TASKS_LIST_PAGE_SIZE):
            message = self._get_task_message()
            messages.append(message)
            if i != constants.TASKS_LIST_PAGE_SIZE - 1:
                self._current_task_index += 1

        return messages

    def _prepare_last_message(self, last_message: OutgoingMessage) -> OutgoingMessage:
        if last_message.bubbles:
            last_message.bubbles.add_row(self._get_control_buttons())
        else:
            bubbles = BubbleMarkup()
            bubbles.add_row(self._get_control_buttons())
            last_message.bubbles = bubbles
        last_message.metadata = {"tasks": self._tasks, "sync_ids": self._sync_ids}
        
        return last_message


    def _get_control_buttons(self) -> List[Button]:
        buttons = []

        if self._current_task_index > 0 and self._current_page > 0:
            buttons.append(
                Button(
                    command="/список",
                    label=f"⬅️ Назад к [{self._current_task_index - 2}-{self._current_task_index - 1}]",
                    data={
                        "current_task_index": self._current_task_index - 2 - self._current_task_index % 2,
                        "current_page": self._current_page - 1
                    },
                )
            )

        if self._current_task_index < len(self._tasks) - 1:
            buttons.append(
                Button(
                    command="/список",
                    label=f"Вперед к [{self._current_task_index + 2}-{self._current_task_index + 3}] ➡️",
                    data={
                        "current_task_index": self._current_task_index + 1,
                        "current_page": self._current_page + 1
                    },
                )
            )

        return buttons

    def _get_task_message(self) -> OutgoingMessage:
        if self._current_task_index > len(self._tasks) - 1:
            return OutgoingMessage(
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                body="У вас больше нет задач",
            )

        task = self._tasks[self._current_task_index]

        bubbles = BubbleMarkup()
        bubbles.add_button(
            command="/expand-task",
            label="Раскрыть задачу полностью",
            data={
                "task_id": task.id,
                "tasks": self._tasks,
                "current_task_index": self._current_task_index,
            },
        )

        if len(task.description) > constants.MAX_PREVIEW_TEXT_LEN:
            task_text = task.description[:constants.MAX_PREVIEW_TEXT_LEN]
        else:
            task_text = task.description

        colleague_id = task.mentioned_colleague_id
        contact = Mention.contact(colleague_id) if colleague_id else "Без контакта"

        return OutgoingMessage(
            bot_id=self._message.bot.id,
            chat_id=self._message.chat.id,
            body=f"**{task.title}**\n\n{task_text}\n\n**Контакт:** {contact}",
            bubbles=bubbles
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


@collector.command(
    "/список",
    description="Посмотреть список задач",
    middlewares=[db_session_middleware],
)
async def get_tasks(message: IncomingMessage, bot: Bot) -> None:
    widget = ListTasksWidget(message)

    if not widget.is_updating:
        task_repo = TaskRepo(message.state.db_session)
        tasks = await task_repo.get_user_tasks(message.sender.huid)
        
        if not tasks:
            await bot.answer_message("У вас нет задач")
            return
        
        await bot.answer_message(
            body=f"**Задач в списке**: {len(tasks)}"
        )

        widget.set_tasks(tasks)

    await widget.send(bot)

@collector.command(
    "/expand-task",
    visible=False,
    middlewares=[db_session_middleware],
)
async def expand_task(message: IncomingMessage, bot: Bot) -> None:
    assert message.source_sync_id

    attachment_repo = AttachmentRepo(message.state.db_session)
    task_repo = TaskRepo(message.state.db_session)
    
    task_id = message.data["task_id"]

    task = await task_repo.get_task(task_id)
    outgoin_attachment = None
    if task.attachment_id:
        attachment = await attachment_repo.get_attachment(task.attachment_id)

        async with file_storage.file(attachment.file_storage_id) as file:
            outgoin_attachment = await OutgoingAttachment.from_async_buffer(file, attachment.filename)

    bubbles = BubbleMarkup()
    bubbles.add_button(
        "/изменить",
        "Изменить описание",
        {"task_id": task.id},
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

    colleague_id = task.mentioned_colleague_id
    contact = Mention.contact(colleague_id) if colleague_id else "Без контакта"

    if outgoin_attachment:
        await bot.answer_message(
            body=f"**{task.title}**\n\n{task.description}\n\n**Контакт:** {contact}",
        )
        if outgoin_attachment:
            await bot.answer_message(body="", bubbles=bubbles, file=outgoin_attachment)
    else:
        await bot.answer_message(
            body=f"**{task.title}**\n\n{task.description}\n\n**Контакт:** {contact}",
            bubbles=bubbles
        )
        