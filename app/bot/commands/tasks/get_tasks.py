from typing import List
from uuid import UUID

from botx import (
    Bot,
    BubbleMarkup,
    Button,
    EditMessage,
    HandlerCollector,
    IncomingMessage,
    OutgoingMessage,
)
from pydantic import parse_obj_as

from app.bot.middlewares.db_session import db_session_middleware
from app.db.task.repo import TaskRepo
from app.resources import strings
from app.schemas.task import Task

collector = HandlerCollector()

MAX_PREVIEW_TEXT_LEN = 100


class ListTasksWidget:
    def __init__(self, message: IncomingMessage):
        self.is_updating = "tasks" in message.metadata

        self._message = message
        self._tasks = parse_obj_as(List[Task], message.metadata.get("tasks", []))
        self._current_task_index = message.data.get("current_task_index", 0)

    def set_tasks(self, tasks: List[Task]) -> None:  # noqa: WPS615
        self._tasks = tasks

    async def send(self, bot: Bot) -> None:
        assert self._tasks, "You must fetch tasks first."

        if self.is_updating:
            await self._update_message(bot)
        else:
            await self._send_message(bot)

    async def _update_message(self, bot: Bot) -> None:
        message = self._outgoing_to_edit_message(
            self._get_task_message(),
            self._message.source_sync_id,
        )
        await bot.edit(message=message)

    async def _send_message(self, bot: Bot) -> None:
        await bot.send(message=self._get_task_message())

    def _get_control_buttons(self) -> List[Button]:
        buttons = []

        if self._current_task_index > 0:
            buttons.append(
                Button(
                    command="/список",
                    label=strings.PREV_TASK_LABEL,
                    data={"current_task_index": self._current_task_index - 1},
                )
            )

        if self._current_task_index < len(self._tasks) - 1:
            buttons.append(
                Button(
                    command="/список",
                    label=strings.NEXT_TASK_LABEL,
                    data={"current_task_index": self._current_task_index + 1},
                )
            )

        return buttons

    def _get_task_message(self) -> OutgoingMessage:
        task = self._tasks[self._current_task_index]

        bubbles = BubbleMarkup()
        bubbles.add_button(
            command="/expand-task",
            label=strings.EXPAND_TASK_LABEL,
            data={
                "task_id": task.id,
                "tasks": self._tasks,
                "current_task_index": self._current_task_index,
            },
        )
        bubbles.add_row(self._get_control_buttons())

        if len(task.text) > MAX_PREVIEW_TEXT_LEN:
            task_text = task.text[:MAX_PREVIEW_TEXT_LEN]
        else:
            task_text = task.text

        return OutgoingMessage(
            bot_id=self._message.bot.id,
            chat_id=self._message.chat.id,
            body=f"**{task.title}**\n\n{task_text}",
            bubbles=bubbles,
            metadata={"tasks": self._tasks},
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
async def get_tasks(message: IncomingMessage, bot: Bot) -> None:  # noqa: WPS463
    widget = ListTasksWidget(message)

    if not widget.is_updating:
        task_repo = TaskRepo(message.state.db_session)
        tasks = await task_repo.get_user_tasks(message.sender.huid)

        if not tasks:
            await bot.send(strings.YOU_HAVE_NO_TASKS_TEXT)
            return

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
    task_id = message.data["task_id"]

    task = await task_repo.get_task(task_id)

    bubbles = BubbleMarkup()
    bubbles.add_button(
        "/список",
        strings.HIDE_TASK_LABEL,
        {
            "task_id": task.id,
            "tasks": message.data["tasks"],
            "current_task_index": message.data["current_task_index"],
        },
    )
    bubbles.add_button(
        "/delete-task",
        strings.DELETE_TASK_LABEL,
        {"task_id": task_id},
    )

    await bot.edit_message(
        bot_id=message.bot.id,
        sync_id=message.source_sync_id,
        body=f"**{task.title}**\n\n{task.text}",
        bubbles=bubbles,
    )
