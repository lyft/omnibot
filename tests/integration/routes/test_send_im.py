import json
from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client

from tests.integration.routes import get_test_bot


def test_send_bot_im(
    internal_client: Client,
    mocker: MockerFixture,
    slack_api_call: MagicMock,
):
    get_im_channel_id = mocker.patch("omnibot.services.slack.get_im_channel_id")
    get_user_by_email = mocker.patch("omnibot.services.slack.get_user_by_email")
    get_user_by_email.return_value = {"id": "TEST_USER_ID"}
    get_im_channel_id.return_value = "TEST_CHANNEL_ID"
    slack_api_call.return_value = {"ok": True}

    resp: Response = internal_client.post(
        "/api/v1/slack/send_im/test-team-name/TEST_OMNIBOT_NAME/testuser@example.com",
        data=json.dumps({"action": "test-send-bot-im", "kwargs": {}}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json == {"ok": True}
    get_user_by_email.assert_called_once_with(get_test_bot(), "testuser@example.com")
    get_im_channel_id.assert_called_once_with(get_test_bot(), "TEST_USER_ID")
    slack_api_call.assert_called_once_with(
        "test-send-bot-im",
        channel="TEST_CHANNEL_ID",
    )
