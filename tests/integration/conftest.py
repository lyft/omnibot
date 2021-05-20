from unittest.mock import MagicMock

import pytest
from flask import testing
from pytest_mock import MockerFixture
from slackclient import SlackClient
from werkzeug.datastructures import Headers
from werkzeug.test import Client

from omnibot.app import app
from omnibot.routes import api

app.register_blueprint(api.blueprint)


class TestClient(testing.FlaskClient):
    """
    Overrides the default Flask test client to apply envoy headers so that the envoy
    checks pass.
    """

    def open(self, *args, **kwargs):
        envoy_test_headers = Headers({"x-envoy-downstream-service-cluster": "envoy"})
        headers = kwargs.pop("headers", Headers())
        headers.extend(envoy_test_headers)
        kwargs["headers"] = headers
        return super().open(*args, **kwargs)


class TestInternalClient(testing.FlaskClient):
    """
    Overrides the default Flask test client to apply internal envoy headers so that the
    authorization checks pass.
    """

    def open(self, *args, **kwargs):
        envoy_test_headers = Headers(
            {
                "x-envoy-downstream-service-cluster": "someservice",
                "x-envoy-internal": "true",
            }
        )
        headers = kwargs.pop("headers", Headers())
        headers.extend(envoy_test_headers)
        kwargs["headers"] = headers
        return super().open(*args, **kwargs)


@pytest.fixture(scope="session")
def client() -> Client:
    """
    Returns a werkzeug compatible Flask test client for testing the full request to
    response flow for all Slack API related omnibot endpoints.
    """
    app.test_client_class = TestClient
    with app.test_client() as c:
        yield c


@pytest.fixture(scope="session")
def internal_client() -> Client:
    """
    Returns a werkzeug compatible Flask test client for testing the full request to
    response flow for all internal-related omnibot endpoints.
    """
    app.test_client_class = TestInternalClient
    with app.test_client() as c:
        yield c


@pytest.fixture
def instrument(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("omnibot.routes.api.instrument_event")


@pytest.fixture
def queue(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("omnibot.routes.api.queue_event")


@pytest.fixture
def slack_api_call(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(SlackClient, "api_call")
