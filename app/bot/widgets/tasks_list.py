"""Widget for displaying a task list."""

from math import ceil
from typing import List
from uuid import UUID

from pybotx import (
    Bot,
    BubbleMarkup,
    Button,
    EditMessage,
    IncomingMessage,
    MentionBuilder,
    OutgoingMessage,
)
from pydantic import parse_obj_as

from app.bot import constants
from app.resources import strings
from app.schemas.tasks import Task


class TasksListWidget:
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
