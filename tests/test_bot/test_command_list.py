import pytest
from botx import Bot
from botx.models.menu import MenuCommand


@pytest.mark.asyncio
async def test_command_sequence(bot: Bot):
    bot_commands = (await bot.status()).result.commands

    command_list = [
        MenuCommand(
            description="Показать список команд",
            body="/help",
            name="help",
            options={},
            elements=[],
        ),
        MenuCommand(
            description="Создать новую задачу", body="/создать", name="create-task"
        ),
        MenuCommand(description="Все мои задачи", body="/список", name="tasks-list"),
        MenuCommand(
            description="Справка по командам", body="/справка", name="tasks-information"
        ),
    ]

    assert bot_commands == command_list
