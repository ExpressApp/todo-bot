from uuid import UUID
from unittest.mock import AsyncMock

import pytest
from pybotx import Bot, UserFromSearch, UserNotFoundError

from app.services.botx_user_search import search_user_on_each_cts, UserIsBotError


async def test_search_user_on_each_cts_user_is_bot_error_raised(
    bot: Bot,
) -> None:
    # - Arrange -
    bot_user = UserFromSearch(
        huid=UUID("86c4814b-feee-4ff0-b04d-4b3226318078"),
        ad_login=None,
        ad_domain=None,
        username="Test Bot",
        company=None,
        company_position=None,
        department=None,
        emails=[],
    )

    bot.search_user_by_huid = AsyncMock(return_value=bot_user)

    # - Act -
    with pytest.raises(UserIsBotError):
        await search_user_on_each_cts(bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078"))


async def test_search_user_on_each_cts_not_found(
    bot: Bot,
) -> None:
    # - Arrange -
    bot.search_user_by_huid = AsyncMock(side_effect=UserNotFoundError("not found"))

    # - Act -
    found_user = await search_user_on_each_cts(bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078"))

    # - Assert -
    assert found_user is None


async def test_search_user_on_each_cts_suceed(
    bot: Bot,
) -> None:
    # - Arrange -
    user = UserFromSearch(
        huid=UUID("86c4814b-feee-4ff0-b04d-4b3226318078"),
        ad_login=None,
        ad_domain=None,
        username="Test User",
        company=None,
        company_position=None,
        department=None,
        emails=[],
    )

    bot.search_user_by_huid = AsyncMock(return_value=user)

    # - Act -
    found_user, bot_account = await search_user_on_each_cts(bot, UUID("86c4814b-feee-4ff0-b04d-4b3226318078"))

    # - Assert -
    assert found_user is user
    assert bot_account is list(bot.bot_accounts)[0]
