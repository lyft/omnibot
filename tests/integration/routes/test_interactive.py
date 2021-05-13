import json

from pytest_mock import MockerFixture
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/interactive"


def test_dialog_submission_echo_test(client: Client):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200


def test_message_action_on_test_message(client: Client, mocker: MockerFixture):
    mocker.patch("omnibot.services.slack.client")
    with get_mock_data("interactive/message_action_on_test_message.json") as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
