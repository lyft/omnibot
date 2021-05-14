import os
from unittest.mock import MagicMock

import boto3
import pytest
from flask import testing
from moto import mock_sqs
from pytest_mock import MockerFixture
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


@pytest.fixture(scope="session")
def client() -> Client:
    """
    Returns a werkzeug compatible Flask test client for testing the full request to
    response flow for all omnibot endpoints.
    """
    app.test_client_class = TestClient
    with app.test_client() as c:
        yield c


@pytest.fixture
def instrument(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("omnibot.routes.api.instrument_event")


@pytest.fixture
def queue(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("omnibot.routes.api.queue_event")


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_sqs():
        yield boto3.client("s3", region_name="us-east-1")
