"""Module for enums."""
from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class TaskApproveCommands(StrEnum):
    YES = "YES"
    NO = "NO"
