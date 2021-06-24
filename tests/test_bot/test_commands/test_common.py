from os import environ

import pytest
from botx.testing import MessageBuilder, TestClient as BotXClient


@pytest.mark.asyncio
async def test_default_handler(builder: MessageBuilder, botx_client: BotXClient):
    text = "random text"
    builder.body = text
    await botx_client.send_command(builder.message)

    assert len(botx_client.command_results) == 0


@pytest.mark.asyncio
async def test_help_command(builder: MessageBuilder, botx_client: BotXClient):
    builder.body = "/help"

    await botx_client.send_command(builder.message)

    body = botx_client.notifications[0].result.body

    assert body == "\n".join(
        (
            "Справка по командам:\n",
            "`/help` - Справка по командам.\n"
            "`/создать` - Создать новую задачу\n"
            "`/список` - Все мои задачи\n"
            "`/справка` - Справка по командам",
        )
    )


@pytest.mark.asyncio
async def test_debug_commit_sha_command(
    builder: MessageBuilder, botx_client: BotXClient
):
    environ["GIT_COMMIT_SHA"] = "test-git-commit-sha"
    builder.body = "/_debug:git-commit-sha"

    await botx_client.send_command(builder.message)

    body = botx_client.notifications[0].result.body

    assert body == "test-git-commit-sha"
