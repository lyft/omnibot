import json
from unittest.mock import MagicMock

import pytest
from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/interactive"


@pytest.fixture
def slackclient(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("omnibot.services.slack.client")


def test_dialog_submission_echo_test(
    client: Client, queue: MagicMock, slackclient: MagicMock
):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        queue.assert_called_once()
        slackclient.assert_not_called()


def test_message_action_on_test_message(
    client: Client, queue: MagicMock, slackclient: MagicMock
):
    with get_mock_data("interactive/message_action_on_test_message.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        queue.assert_not_called()
        slackclient.assert_called_once()
