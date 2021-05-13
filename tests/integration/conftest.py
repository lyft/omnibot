import pytest
from werkzeug.test import Client

from flask import testing
from werkzeug.datastructures import Headers
from omnibot.app import app
from omnibot.routes import api

app.register_blueprint(api.blueprint)


class TestClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        envoy_test_headers = Headers({"x-envoy-downstream-service-cluster": "envoy"})
        headers = kwargs.pop("headers", Headers())
        headers.extend(envoy_test_headers)
        kwargs["headers"] = headers
        return super().open(*args, **kwargs)


@pytest.fixture(scope="session")
def client() -> Client:
    app.test_client_class = TestClient
    with app.test_client() as c:
        yield c
