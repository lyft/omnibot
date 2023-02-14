import json
from typing import Any
from typing import Dict
from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from werkzeug.test import Client

from tests.data import get_mock_data
from tests.integration.routes import get_test_bot

_ENDPOINT = "/api/v1/slack/event"


def test_url_verification(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/url_verification.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT,
            data=json_data,
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert (
            resp.json["challenge"]
            == "ABCDEFGHIJKLMNOPQRSTUVWXABCDEFGHIJKLMNOPQRSTUVWX1234"
        )
        instrument.assert_not_called()
        queue.assert_not_called()


def test_event_callback_omnibot_help(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        event: Dict[str, Any] = json.loads(json_data.read())
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(event),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        instrument.assert_called_once_with(get_test_bot(), event)
        queue.assert_called_once_with(get_test_bot(), event, "event")


def test_event_callback_test_message(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/event_callback_test_message.json") as json_data:
        event: Dict[str, Any] = json.loads(json_data.read())
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(event),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        instrument.assert_called_once_with(get_test_bot(), event)
        queue.assert_called_once_with(get_test_bot(), event, "event")


def test_misisng_verification_token(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/url_verification.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("token", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No verification token in event."
        instrument.assert_not_called()
        queue.assert_not_called()


def test_invalid_verification_token(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/url_verification.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["token"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "url_verification failed."
        instrument.assert_not_called()
        queue.assert_not_called()


def test_missing_app_id(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("api_app_id", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No api_app_id in event."
        instrument.assert_not_called()
        queue.assert_not_called()


def test_missing_team_id(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("team_id", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "No team_id in event."
        instrument.assert_not_called()
        queue.assert_not_called()


def test_invalid_team(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["team_id"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "Unsupported team"
        instrument.assert_not_called()
        queue.assert_not_called()


def test_invalid_bot(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["api_app_id"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "ignored"
        assert resp.json["warning"] == "Unsupported bot"
        instrument.assert_not_called()
        queue.assert_not_called()


def test_invalid_verification_token_for_valid_bot(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data["token"] = "something random"
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert resp.json["error"] == "Incorrect verification token in event for bot"
        instrument.assert_not_called()
        queue.assert_not_called()


def test_event_missing_event_block(
    client: Client,
    instrument: MagicMock,
    queue: MagicMock,
):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        modified_data: Dict[str, Any] = json.loads(json_data.read())
        modified_data.pop("event", None)
        resp: Response = client.post(
            _ENDPOINT,
            data=json.dumps(modified_data),
            content_type="application/json",
        )
        assert resp.status_code == 403
        assert resp.json["status"] == "failure"
        assert (
            resp.json["error"]
            == "Request does not have an event. Processing will not proceed!"
        )
        instrument.assert_not_called()
        queue.assert_not_called()
