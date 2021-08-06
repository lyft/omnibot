from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client

from tests.integration.routes import get_test_bot


def test_get_channel_by_name(internal_client: Client, mocker: MockerFixture):
    get_channel_by_name = mocker.patch("omnibot.services.slack.get_channel_by_name")
    mock_channel_value = {"channel": {"id": "test-channel-id"}}
    get_channel_by_name.return_value = mock_channel_value
    resp: Response = internal_client.get(
        "/api/v1/slack/get_channel/test-team-name/TEST_OMNIBOT_NAME/test-channel"
    )
    assert resp.status_code == 200
    assert resp.json == mock_channel_value
    get_channel_by_name.assert_called_once_with(get_test_bot(), "test-channel")


def test_get_channel_by_name_invalid(internal_client: Client, mocker: MockerFixture):
    get_channel_by_name = mocker.patch("omnibot.services.slack.get_channel_by_name")
    get_channel_by_name.return_value = None
    resp: Response = internal_client.get(
        "/api/v1/slack/get_channel/test-team-name/TEST_OMNIBOT_NAME/test-channel"
    )
    assert resp.status_code == 404
    assert resp.json["error"] == "provided channel_name was not found."
    get_channel_by_name.assert_called_once_with(get_test_bot(), "test-channel")
