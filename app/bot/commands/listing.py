"""For using bot commands as enum."""

from enum import auto
from typing import List

from pydantic import BaseModel

from app.resources import strings
from app.schemas.enums import StrEnum


class HiddenCommand(BaseModel):
    """For using hidden command as object, not just strings."""

    command: str
    name: str

    def __getitem__(self, key: str) -> str:
        """Return values by [] syntax.

        This is used by dict unpacking (**).
        """

        return getattr(self, key)

    def keys(self) -> List[str]:
        """Return value by keys."""

        return ["command", "name"]


class Command(HiddenCommand):
    """For using command as object, not just strings."""

    description: str

    def keys(self) -> List[str]:
        """Return value by keys."""

        return [*super().keys(), "description"]


class CommandsEnum:
    CREATE_TASK = Command(
        command="/создать",
        name="create-task",
        description=strings.CREATE_TASK_DESCRIPTION,
    )
    TASK_LIST = Command(
        command="/список",
        name="tasks-list",
        description=strings.TASK_LIST_DESCRIPTION,
    )
    COMMANDS_HELP = Command(
        command="/справка",
        name="tasks-information",
        description=strings.TASKS_INFORMATION_DESCRIPTION,
    )
    EXPAND_TASK = HiddenCommand(
        command="/раскрыть",
        name="expand-task",
    )
    EDIT_TASK = HiddenCommand(
        command="/изменить",
        name="change-task",
    )
    EDIT_TITLE = HiddenCommand(
        command="/изменить-заголовок",
        name="change-task-title",
    )
    EDIT_DESCRIPTION = HiddenCommand(
        command="/изменить-описание",
        name="change-task-description",
    )
    EDIT_MENTION = HiddenCommand(
        command="/изменить-упоминание",
        name="change-task-mention",
    )
    EDIT_ATTACHMENT = HiddenCommand(
        command="/изменить-вложение",
        name="change-task-attachment",
    )
    DELETE_TASK = HiddenCommand(
        command="/удалить",
        name="delete-task",
    )


class FSMCommandsEnum(StrEnum):
    def _generate_next_value_(  # type: ignore  # noqa: WPS120
        name, start, count, last_values  # noqa: N805
    ):
        return f"FSM:{name}"

    YES = auto()
    NO = auto()
    SKIP_INPUT = auto()
    CANCEL_PROCESS = auto()
    EDIT_TITLE = auto()
    EDIT_DESCRIPTION = auto()
    EDIT_MENTION = auto()
    EDIT_ATTACHMENT = auto()
    EDIT_TASK = auto()
    MESSAGE_AS_TITLE = auto()
    MESSAGE_AS_DESCRIPTION = auto()
