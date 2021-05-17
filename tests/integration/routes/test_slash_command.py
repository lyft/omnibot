import json
from typing import Dict, Any  # noqa: F401
from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from werkzeug.test import Client

from tests.data import get_mock_data
from tests.integration.routes import get_test_bot

_ENDPOINT = "/api/v1/slack/slash_command"


def test_user_issues_echo_command(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        event: Dict[str, Any] = json.loads(json_data.read())
        resp: Response = client.post(
            _ENDPOINT,
            data=event,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        command = event.copy()
        command["omnibot_bot_id"] = "TEST_OMNIBOT_ID"
        queue.assert_called_once_with(get_test_bot(), command, "slash_command")
        assert resp.json["response_type"] == "in_channel"


def test_missing_token(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("token", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=modified_data,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No verification token in slash command."
        queue.assert_not_called()


def test_missing_team_id(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("team_id", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=modified_data,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No team_id in slash command."
        queue.assert_not_called()


def test_invalid_verification_token(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["token"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=modified_data,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert (
            resp.json["error"]
            == "Token sent with slash command does not match any configured app."
        )
        queue.assert_not_called()


def test_unsupported_team(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["team_id"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=modified_data,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "Unsupported team"
        queue.assert_not_called()


def test_missing_handler(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["command"] = "/somethingrandom"
        resp: Response = client.post(
            _ENDPOINT,
            data=modified_data,
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        assert resp.json["response_type"] == "ephemeral"
        assert (
            resp.json["text"]
            == "This slash command does not have any omnibot handler associated with it."  # noqa: E501
        )
        queue.assert_not_called()
