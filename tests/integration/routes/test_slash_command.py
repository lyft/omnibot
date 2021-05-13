import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/slash_command"


def test_user_issues_echo_command(client: Client):
    with get_mock_data(
        "slash_command/user_issues_echo_command.json"
    ) as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT,
            data=json.loads(json_data.read()),
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
