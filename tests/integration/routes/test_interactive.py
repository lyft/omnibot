import json
from typing import Any, Dict  # noqa: F401
from unittest.mock import MagicMock, call

import pytest
from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from slackclient import SlackClient
from werkzeug.test import Client

from tests.data import get_mock_data
from tests.integration.routes import get_test_bot

_ENDPOINT = "/api/v1/slack/interactive"


@pytest.fixture
def slack_api_call(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(SlackClient, "api_call")


def test_dialog_submission_echo_test(
    client: Client, queue: MagicMock, slack_api_call: MagicMock
):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        event: Dict[str, Any] = json.loads(json_data.read())
        resp: Response = client.post(
            _ENDPOINT,
            data=event,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200

        component = json.loads(event["payload"])
        component["omnibot_bot_id"] = "TEST_OMNIBOT_ID"
        queue.assert_called_once_with(
            get_test_bot(), component, "interactive_component"
        )
        slack_api_call.assert_not_called()


def test_message_action_on_test_message(
    client: Client, queue: MagicMock, slack_api_call: MagicMock
):
    with get_mock_data("interactive/message_action_on_test_message.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        assert resp.json["response_type"] == "in_channel"
        queue.assert_not_called()
        slack_api_call.assert_called_once_with(
            "dialog.open",
            dialog={
                "title": "Echo dialog",
                "submit_label": "submit",
                "callback_id": "echo_dialog_1",
                "elements": [
                    {"type": "text", "label": "Echo this text", "name": "echo_element"}
                ],
            },
            trigger_id="TEST_TRIGGER_ID",
        )


def test_invalid_component_type(
    client: Client, queue: MagicMock, slack_api_call: MagicMock
):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data["type"] = "not a valid type"
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 400
        assert resp.json["status"] == "failure"
        assert (
            resp.json["error"]
            == "Unsupported type=not a valid type in interactive component."
        )
        queue.assert_not_called()
        slack_api_call.assert_not_called()


def test_missing_token(client: Client, queue: MagicMock, slack_api_call: MagicMock):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data.pop("token", None)
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No verification token in interactive component."
        queue.assert_not_called()
        slack_api_call.assert_not_called()


def test_missing_team(client: Client, queue: MagicMock, slack_api_call: MagicMock):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data.pop("team", None)
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No team id in interactive component."
        queue.assert_not_called()
        slack_api_call.assert_not_called()


def test_unsupported_team(client: Client, queue: MagicMock, slack_api_call: MagicMock):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data["team"]["id"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "Unsupported team"
        queue.assert_not_called()
        slack_api_call.assert_not_called()


def test_invalid_token(client: Client, queue: MagicMock, slack_api_call: MagicMock):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data["token"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert (
            resp.json["error"]
            == "Token sent with interactive component does not match any configured app."  # noqa: E501
        )
        queue.assert_not_called()
        slack_api_call.assert_not_called()


def test_invalid_callback_id(
    client: Client, queue: MagicMock, slack_api_call: MagicMock
):
    with get_mock_data("interactive/dialog_submission_echo_test.json") as json_data:
        payload: Dict[str, Any] = json.loads(json_data.read())
        modified_data: Dict[str, Any] = json.loads(payload["payload"])
        modified_data["callback_id"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data={"payload": json.dumps(modified_data)},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        assert resp.json["response_type"] == "ephemeral"
        assert (
            resp.json["text"]
            == "This interactive component does not have any omnibot handler associated with it."  # noqa: E501
        )
        queue.assert_not_called()
        slack_api_call.assert_not_called()
