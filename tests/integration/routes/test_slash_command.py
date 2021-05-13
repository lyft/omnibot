import json
from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from werkzeug.test import Client

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/slash_command"


def test_user_issues_echo_command(client: Client, queue: MagicMock):
    with get_mock_data("slash_command/user_issues_echo_command.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        queue.assert_called_once()
        assert resp.json["response_type"] == "in_channel"
