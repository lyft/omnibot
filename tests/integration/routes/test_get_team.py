from flask import Response  # noqa: F401
from werkzeug.test import Client


def test_get_team_id_by_name(internal_client: Client):
    resp: Response = internal_client.get("/api/v1/slack/get_team/test-team-name")
    assert resp.status_code == 200
    assert resp.json["team_id"] == "TEST_TEAM_ID"


def test_get_team_id_by_name_invalid(internal_client: Client):
    resp: Response = internal_client.get(
        "/api/v1/slack/get_team/test-invalid-team-name"
    )
    assert resp.status_code == 404
    assert resp.json["error"] == "provided team_name is not configured."
