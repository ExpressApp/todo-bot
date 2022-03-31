from typing import List, Optional
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
from pybotx_smart_logger.logger import smart_log
from pydantic import parse_obj_as

from app.bot.middlewares.db_session import db_session_middleware
from app.db.task.repo import TaskRepo
from app.schemas.tasks import Task

collector = HandlerCollector()

MAX_PREVIEW_TEXT_LEN = 100


class ListTasksWidget:
    def __init__(self, message: IncomingMessage):
        self.is_updating = "tasks" in message.metadata

        self._sync_id = parse_obj_as(Optional[UUID], message.metadata.get("sync_id", None))
        self._message = message
        self._tasks = parse_obj_as(List[Task], message.metadata.get("tasks", []))
        
        self._current_task_index = message.data.get("current_task_index", 0)
        self._current_page = message.data.get("current_page", 0)

        self._last_in_page = False

    def set_tasks(self, tasks: List[Task]) -> None:  # noqa: WPS615
        self._tasks = tasks

    async def send(self, bot: Bot) -> None:
        assert self._tasks, "You must fetch tasks first."

        if self.is_updating:
            await self._update_message(bot, self._sync_id)

            # Костыль
            self._current_task_index += 1
            self._last_in_page = True

            await self._update_message(bot)
            # Костыль
            self._last_in_page = False
        else:
            await self._send_message(bot)

    async def _update_message(self, bot: Bot, sync_id: Optional[UUID]=None) -> None:
        if not sync_id:
            sync_id = self._message.source_sync_id
        message = self._outgoing_to_edit_message(
            self._get_task_message(),
            sync_id,
        )
        await bot.edit(message=message)

    async def _send_message(self, bot: Bot) -> None:
        sync_id = await bot.send(message=self._get_task_message())
        self._sync_id = sync_id
        
        # Костыль
        self._current_task_index += 1
        self._last_in_page = True
        
        await bot.send(message=self._get_task_message())
        # Костыль
        self._last_in_page = False

    def _get_control_buttons(self) -> List[Button]:
        buttons = []

        if self._current_task_index > 0 and self._current_page > 0:
            buttons.append(
                Button(
                    command="/список",
                    label=f"Назад к [{self._current_task_index - 2}-{self._current_task_index - 1}]",
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
                    label=f"Вперед к [{self._current_task_index + 2}-{self._current_task_index + 3}]",
                    data={
                        "current_task_index": self._current_task_index + 1,
                        "current_page": self._current_page + 1
                    },
                )
            )

        return buttons

    def _get_task_message(self) -> OutgoingMessage:
        # Можно и нужно сделать лучше
        if self._current_task_index > len(self._tasks) - 1:
            bubbles = BubbleMarkup()
            if self._last_in_page:
                bubbles.add_row(self._get_control_buttons())
            return OutgoingMessage(
                bot_id=self._message.bot.id,
                chat_id=self._message.chat.id,
                body="У вас больше нет задач",
                bubbles=bubbles,
                metadata={"tasks": self._tasks, "sync_id": self._sync_id}
            )

        task = self._tasks[self._current_task_index]

        bubbles = BubbleMarkup()
        bubbles.add_button(
            command="/expand-task",
            label="Подробнее",
            data={
                "task_id": task.id,
                "tasks": self._tasks,
                "current_task_index": self._current_task_index,
            },
        )
        if self._last_in_page:
            bubbles.add_row(self._get_control_buttons())

        if len(task.description) > MAX_PREVIEW_TEXT_LEN:
            task_text = task.description[:MAX_PREVIEW_TEXT_LEN]
        else:
            task_text = task.description

        return OutgoingMessage(
            bot_id=self._message.bot.id,
            chat_id=self._message.chat.id,
            body=f"**{task.title}**\n\n{task_text}",
            bubbles=bubbles,
            metadata={"tasks": self._tasks, "sync_id": self._sync_id},
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
            await bot.send("У вас нет задач")
            return

        widget.set_tasks(tasks)

    await widget.send(bot)
