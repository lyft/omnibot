from flask import Response  # noqa: F401
from werkzeug.test import Client


def test_healthcheck(client: Client):
    resp: Response = client.get("/healthcheck")
    assert resp.status_code == 200
