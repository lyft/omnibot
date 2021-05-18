import json

from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client


def test_get_bot_ims(internal_client: Client, mocker: MockerFixture):
    get_ims = mocker.patch("omnibot.services.slack.get_ims")
    mock_im = {
        "id": "TEST_IM_ID",
        "created": 0,
        "is_im": True,
        "is_org_shared": True,
        "user": "TEST_USER_ID",
        "is_user_deleted": False,
        "priority": 0,
    }
    mock_ims_value = [
        (
            "TEST_IM_ID",
            json.dumps(mock_im),
        )
    ]
    get_ims.return_value = mock_ims_value
    resp: Response = internal_client.get(
        "/api/v1/slack/get_ims/test-team-name/TEST_OMNIBOT_NAME"
    )
    assert resp.status_code == 200
    assert resp.json == {"ims": [mock_im]}
