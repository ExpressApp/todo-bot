"""Text and templates for messages and api responses."""
from pathlib import Path
from typing import Any, Protocol, cast

from mako.lookup import TemplateLookup


class FormatTemplate(Protocol):
    """
    Protocol for correct templates typing.

    Allow use format() instead of render() method that needed to maintain consistency
    with regular string formatting.
    """

    def format(self, **kwargs: Any) -> str:  # noqa: WPS125 A003
        """Render templates."""


class TemplateFormatterLookup(TemplateLookup):
    """Represent a collection of templates from the local filesystem."""

    def get_template(self, uri: str) -> FormatTemplate:
        """Cast default mako templates to FormatTemplate."""

        def _format(**kwargs: Any) -> str:  # noqa: WPS430
            return template.render(**kwargs).rstrip()

        template = super().get_template(uri)
        template.format = _format  # noqa: WPS125
        return cast(FormatTemplate, template)


lookup = TemplateFormatterLookup(
    directories=["app/resources/templates"], input_encoding="utf-8"
)

texts_path = Path("app/resources/texts")


def read_text(filename: str) -> str:
    """Read text from resources."""

    return texts_path.joinpath(filename).read_text().strip()


BOT_NAME = "to-do-bot"

HELP_COMMAND_MESSAGE_TEMPLATE = lookup.get_template("help.txt.mako")
HELP_COMMAND_DESCRIPTION = "Показать список команд"
HELP_LABEL = "/help"

YES_LABEL = "Да"
NO_LABEL = "Нет"
SKIP_INPUT_LABEL = "Пропустить"
CANCEL_LABEL = "Отмена"

# Service screens
MENTION_VALIDATION_ERROR = read_text("mention_validation.md")
TEXT_WHEN_FILE_REQUIRED_ERROR = read_text("input_text_when_file_required.md")
FILE_WHEN_TITLE_REQUIRED_ERROR = read_text("file_when_text_title_required.md")
FILE_WHEN_DESCRIPTION_REQUIRED_ERROR = read_text(
    "file_when_text_description_required.md"
)

CANCEL_EDIT_TASK_TEXT = read_text("cancel_edit_task.md")

CREATE_TASK_LABEL = "Создать задачу"
TASK_LIST_LABEL = "Посмотреть список задач"
RETURN_TO_TASK_LIST_LABEL = " Вернуться к списку задач"

TASK_LIST_DESCRIPTION = "Все мои задачи"
CHAT_CREATED_TEXT = lookup.get_template("chat_created.txt.mako")
CREATE_TASK_DESCRIPTION = "Создать новую задачу"
TASKS_INFORMATION_DESCRIPTION = "Справка по командам"

DEFAULT_MESSAGE_TEXT = read_text("default_message.md")
COMMANDS_HELP_TEXT = read_text("commands_help.md")

INPUT_TITLE_TEXT = read_text("input_title.md")
INPUT_DESCRIPTION_TEXT = read_text("input_description.md")
INPUT_MENTION_TEXT = read_text("input_mention.md")

INPUT_ATTACHMENT_TEXT = read_text("input_attachment.md")

ATTACHMENT_NOT_SUPPORT_TEXT = read_text("attachment_not_support.md")

CHECKING_DATA_TEXT = read_text("checking_data.md")
RE_CHECKING_DATA_TEXT = read_text("re_checking_data.md")
FULL_TASK_DESCRIPTION_TEMPLATE = lookup.get_template("full_task_description.md.mako")

SUCCESSFUL_CREATING_TASK_TEXT = read_text("successful_creating_task.md")

CANCEL_TASK_CREATION_TEXT = read_text("cancel_task_creation.md")

TASK_LIST_COUNT_TEXT = lookup.get_template("task_list_count.md.mako")

TASK_LIST_TEXT = lookup.get_template("task_list.md.mako")
EMPTY_TASK_LIST_TEXT = (
    "У вас нет созданных задач.\nЧтобы создать задачу, нажмите на кнопку:"
)

EXPAND_TASK_LABEL = "Раскрыть задачу полностью"
EXPAND_TASK_MESSAGE = lookup.get_template("expand_task.md.mako")

EDIT_TASK_LABEL = "Изменить"
EDIT_TASK_MESSAGE = "Что необходимо изменить?"

DELETE_TASK_LABEL = "Удалить"
DELETE_TASK_MESSAGE = read_text("successful_deletion_task.md")

EDIT_TITLE_LABEL = "Название задачи"
EDIT_TITLE_MESSAGE = read_text("edit_title.md")
SUCCESSFUL_EDIT_TITLE_MESSAGE = "Заголовок успешно изменен."

EDIT_DESCRIPTION_LABEL = "Описание задачи"
EDIT_DESCRIPTION_MESSAGE = read_text("edit_description.md")
SUCCESSFUL_EDIT_DESCRIPTION_MESSAGE = "Описание успешно изменено."

EDIT_MENTION_IF_NOT_EXIST_LABEL = "Добавить отметку коллеги"
EDIT_MENTION_IF_EXIST_LABEL = "Удалить отметку коллеги"
ADD_MENTION_MESSAGE = read_text("add_mention.md")
SUCCESSFUL_DELETE_MENTION_MESSAGE = "Отметка коллеги успешно удалена."
SUCCESSFUL_ADD_MENTION_MESSAGE = "Отметка коллеги успешно добавлена."

EDIT_ATTACHMENT_IF_NOT_EXIST_LABEL = "Добавить вложение"
EDIT_ATTACHMENT_IF_EXIST_LABEL = "Удалить вложение"
ADD_ATTACHMENT_MESSAGE = read_text("add_attachment.md")
SUCCESSFUL_DELETE_ATTACHMENT_MESSAGE = "Файл успешно удален."
SUCCESSFUL_ADD_ATTACHMENT_MESSAGE = "Файл успешно добавлен."

MUST_PUSH_BUTTON_FOR_EDITING = read_text("must_push_button_for_editing.md")
TASK_NOT_EXIST = read_text("task_not_exist.md")

# Forward message
DECISION_CREATE_TASK_MESSAGE = "Вы хотите создать задачу?"
AS_TITLE_OR_DESCRIPTION = "Пересланное сообщение будет использоваться в качестве:"
AS_TITLE_LABEL = "Названия задачи"
AS_DESCRIPTION_LABEL = "Описания задачи"
TEXT_WHEN_COMMAND_REQUIRED_ERROR = (
    "Вам необходимо завершить создание задачи. Для отмены нажмите кнопку клавиатуры "
    "“Отмена”. "
)

# Warnings
BOT_CANT_COMMUNICATE_WITH_OTHERS_CTS = "\n".join(
    [
        "Данный бот зарегистрирован на другом CTS.",
        "Для продолжения работы напишите боту со своего CTS.",
        "Найти его можно через поиск корпоративных контактов.",
    ]
)

SOMETHING_GOES_WRONG = "\n".join(
    [
        "При обработке сообщения или нажатия на кнопку произошла непредвиденная ошибка.",
        "Пожалуйста, сообщите об этом вашему администратору бота.",
    ]
)

# ====Calendar====
MONTHS = {  # noqa: WPS407
    1: "Янв",
    2: "Фев",
    3: "Мар",
    4: "Апр",
    5: "Май",
    6: "Июн",
    7: "Июл",
    8: "Авг",
    9: "Сен",
    10: "Окт",
    11: "Ноя",
    12: "Дек",
}
WEEKDAYS = (
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс",
)
CAL_DATE_SKIPPED = "Дата пропущена"
SKIP = "Пропустить"
CANCEL = "Отмена"
CAL_DATE_SELECTED = "Дата выбрана"
SELECT_CALENDAR = "Выберите календарь"
SELECT_DATE = "Выберите дату"
# ========

SELECTED_VALUE_LABEL = "{label} {selected_val}"

LEFT_ARROW = "⬅️"
RIGHT_ARROW = "➡️"
UP_ARROW = "⬆️"
DOWN_ARROW = "⬇️"

CHECKBOX_CHECKED = "☑"
CHECKBOX_UNCHECKED = "☐"
CHECK_MARK = "✔️"
ENVELOPE = "✉️"
PENCIL = "✏️"
CROSS_MARK = "❌"

PAGINATION_BACKWARD_BTN_TEMPLATE = f"{LEFT_ARROW} Назад к [{{0}}-{{1}}]"
PAGINATION_FORWARD_BTN_TEMPLATE = lookup.get_template("pagination_forward_btn.txt.mako")

EMPTY_MSG_SYMBOL = "-"
LIST_END = "Конец списка"
