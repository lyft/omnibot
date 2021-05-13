import pytest
from werkzeug.test import Client

from omnibot.app import app
from omnibot.routes import api
app.register_blueprint(api.blueprint)


@pytest.fixture
def client() -> Client:
    with app.test_client() as c:
        yield c
