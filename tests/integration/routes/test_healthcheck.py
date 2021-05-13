from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


def test_healthcheck(client: Client):
    resp: BaseResponse = client.get("/healthcheck")
    assert resp.status_code == 200
