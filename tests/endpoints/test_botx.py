from http import HTTPStatus
from typing import Dict
from uuid import UUID

import respx
from fastapi.testclient import TestClient
from pybotx import Bot

from app.main import get_application


@respx.mock
def test__web_app__bot_status_response_ok(
    bot_id: UUID,
    bot: Bot,
) -> None:
    # - Arrange -
    query_params = {
        "bot_id": str(bot_id),
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "result": {
            "commands": [
                {
                    "body": "/help",
                    "description": "Get available commands",
                    "name": "/help",
                },
                {
                    "body": "/создать",
                    "description": "Создать новую задачу",
                    "name": "/создать",
                },
                {
                    "body": "/список",
                    "description": "Посмотреть список задач",
                    "name": "/список",
                },
            ],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }


@respx.mock
def test__web_app__bot_status_unknown_bot_response_service_unavailable(
    bot_id: UUID,
    bot: Bot,
) -> None:
    # - Arrange -
    query_params = {
        "bot_id": "f3e176d5-ff46-4b18-b260-25008338c06e",
        "chat_type": "chat",
        "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.get(
            "/status",
            params=query_params,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == "Unknown bot_id: f3e176d5-ff46-4b18-b260-25008338c06e"



@respx.mock
def test__web_app__unknown_bot_response_service_unavailable(
    bot: Bot,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "c755e147-30a5-45df-b46a-c75aa6089c8f",
        "command": {
            "body": "/debug",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }

    # - Act -
    with TestClient(get_application()) as test_client:
        response = test_client.post(
            "/command",
            json=payload,
        )

    # - Assert -
    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    status_message = response.json()["error_data"]["status_message"]
    assert status_message == (
        "No credentials for bot c755e147-30a5-45df-b46a-c75aa6089c8f"
    )
