from unittest.mock import MagicMock

from flask import Response  # noqa: F401
from werkzeug.test import Client

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/event"


def test_url_verification(client: Client, instrument: MagicMock, queue: MagicMock):
    with get_mock_data("event/url_verification.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200
        assert (
            resp.json["challenge"]
            == "ABCDEFGHIJKLMNOPQRSTUVWXABCDEFGHIJKLMNOPQRSTUVWX1234"
        )
        instrument.assert_not_called()
        queue.assert_not_called()


def test_event_callback_omnibot_help(
    client: Client, instrument: MagicMock, queue: MagicMock
):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        instrument.assert_called_once()
        queue.assert_called_once()


def test_event_callback_test_message(
    client: Client, instrument: MagicMock, queue: MagicMock
):
    with get_mock_data("event/event_callback_test_message.json") as json_data:
        resp: Response = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        instrument.assert_called_once()
        queue.assert_called_once()
