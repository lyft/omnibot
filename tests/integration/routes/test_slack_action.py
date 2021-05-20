import json
from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client

from tests.integration.routes import get_test_bot


def test_slack_action(
    internal_client: Client, mocker: MockerFixture, slack_api_call: MagicMock
):
    mock_channel_value = {"id": "TEST_CHANNEL_ID", "name": "test-channel"}

    get_channel_by_name = mocker.patch("omnibot.services.slack.get_channel_by_name")
    get_user_by_name = mocker.patch("omnibot.services.slack.get_user_by_name")
    get_channel_by_name.return_value = mock_channel_value
    get_user_by_name.return_value = {
        "profile": {"display_name": "testuser"},
        "id": "test_user_id",
    }
    slack_api_call.return_value = {"ok": True}

    resp: Response = internal_client.post(
        "/api/v2/slack/action/test-team-name/TEST_OMNIBOT_NAME",
        data=json.dumps(
            {
                "action": "chat.postMessage",
                "kwargs": {
                    "channel": "TEST_CHANNEL_ID",
                    "text": "@example see #general and use @here",
                    "as_user": True,
                    "omnibot_parse": {"text": ["channels", "users", "specials"]},
                },
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json == {"ok": True}
    get_channel_by_name.assert_called_once_with(get_test_bot(), "#general")
    get_user_by_name.assert_called_once_with(get_test_bot(), "@example")
    slack_api_call.assert_called_once_with(
        "chat.postMessage",
        channel="TEST_CHANNEL_ID",
        text="<@test_user_id|testuser> see #general and use <!here|here>",
        as_user=True,
    )
