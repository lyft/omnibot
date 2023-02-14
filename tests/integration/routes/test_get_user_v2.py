from flask import Response  # noqa: F401
from pytest_mock import MockerFixture
from werkzeug.test import Client

from tests.integration.routes import get_test_bot


def test_get_user_v2_user_found(internal_client: Client, mocker: MockerFixture):
    get_user_by_email = mocker.patch("omnibot.services.slack.get_user_by_email")
    get_user_by_email.return_value = {
        "profile": {"display_name": "testuser"},
        "id": "test_user_id",
    }
    resp: Response = internal_client.get(
        "/api/v1/slack/get_user/test-team-name/TEST_OMNIBOT_NAME/testuser@test.com",
    )
    assert resp.status_code == 200
    user_resp = resp.json["user"]
    assert user_resp["email"] == "testuser@test.com"
    assert user_resp["name"] == "testuser"
    assert user_resp["team_id"] == "TEST_TEAM_ID"
    assert user_resp["user_id"] == "test_user_id"
    get_user_by_email.assert_called_once_with(get_test_bot(), "testuser@test.com")


def test_get_user_v2_user_not_found(internal_client: Client, mocker: MockerFixture):
    get_user_by_email = mocker.patch("omnibot.services.slack.get_user_by_email")
    get_user_by_email.return_value = None
    resp: Response = internal_client.get(
        "/api/v1/slack/get_user/test-team-name/TEST_OMNIBOT_NAME/notauser@test.com",
    )
    assert resp.status_code == 404
    assert resp.json["error"] == "user not found"
    get_user_by_email.assert_called_once_with(get_test_bot(), "notauser@test.com")
