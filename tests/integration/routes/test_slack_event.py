import pytest
from pytest_mock import MockerFixture
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from tests.data import get_mock_data

_ENDPOINT = "/api/v1/slack/event"


@pytest.fixture(autouse=True)
def mock_queue_event(mocker: MockerFixture):
    mocker.patch("omnibot.routes.api.instrument_event")
    mocker.patch("omnibot.routes.api.queue_event")


def test_url_verification(client: Client):
    with get_mock_data("event/url_verification.json") as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200


def test_event_callback_omnibot_help(client: Client):
    with get_mock_data("event/event_callback_omnibot_help.json") as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200


def test_event_callback_test_message(client: Client):
    with get_mock_data("event/event_callback_test_message.json") as json_data:
        resp: BaseResponse = client.post(
            _ENDPOINT, data=json_data, content_type="application/json"
        )
        assert resp.status_code == 200
