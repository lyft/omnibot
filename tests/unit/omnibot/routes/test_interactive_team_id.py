import json
import logging
import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import Flask

from omnibot.routes.api import blueprint as api_blueprint
from omnibot.services.slack.bot import Bot
from omnibot.services.slack.team import Team

logger = logging.getLogger(__name__)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(TESTS_DIR)))),
    "data",
    "mock",
    "interactive",
)


def load_test_payload(filename="interactive_enterprise.json"):
    with open(os.path.join(MOCK_DIR, filename)) as f:
        return json.load(f)


@pytest.fixture
def app():
    """Create test Flask app with blueprint."""
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_team():
    team = MagicMock(spec=Team)
    team.team_id = "T00000000"
    team.logging_context = {"team_id": "T00000000"}
    return team


@pytest.fixture
def mock_bot(mock_team):
    bot = MagicMock(spec=Bot)
    bot.verification_token = "test_token_123"
    bot.team = mock_team
    bot.bot_id = "B00000000"
    bot.name = "testbot"
    bot.logging_context = {"team_id": "T00000000", "bot_id": "B00000000"}
    bot.interactive_component_handlers = [
        {
            "callback_id": "test_events",
            "no_message_response": True,
        },
    ]
    return bot


@pytest.fixture
def mock_get_team(mock_team):
    with patch("omnibot.services.slack.team.Team.get_team_by_id") as mock:
        mock.return_value = mock_team
        yield mock


@pytest.fixture
def mock_get_bot(mock_bot):
    with patch("omnibot.services.slack.bot.Bot.get_bot_by_verification_token") as mock:
        mock.return_value = mock_bot
        yield mock


@pytest.fixture
def mock_auth_checks():
    with patch(
        "omnibot.authnz.envoy_checks.envoy_internal_check",
    ) as internal_check, patch(
        "omnibot.authnz.envoy_checks.envoy_permissions_check",
    ) as permissions_check:
        internal_check.return_value = True
        permissions_check.return_value = True
        yield


def test_enterprise_install_original_message_team(
    client,
    mock_get_team,
    mock_get_bot,
    mock_auth_checks,
):
    """Test team ID lookup prioritizes original_message.team for enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = True
    payload["team"] = None
    payload["original_message"]["team"] = "T00000000"
    payload["user"]["team_id"] = "T11111111"

    response = client.post(
        "/api/v1/slack/interactive",
        data={"payload": json.dumps(payload)},
        headers={
            "x-envoy-internal": "true",
            "x-envoy-downstream-service-cluster": "test-service",
        },
    )

    assert response.status_code == 200
    mock_get_team.assert_called_once_with("T00000000")


def test_enterprise_install_user_team_id_fallback(
    client,
    mock_get_team,
    mock_get_bot,
    mock_auth_checks,
):
    """Test team ID lookup falls back to user.team_id for enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = True
    payload["team"] = None
    payload["original_message"]["team"] = None
    payload["user"]["team_id"] = "T00000000"

    response = client.post(
        "/api/v1/slack/interactive",
        data={"payload": json.dumps(payload)},
        headers={
            "x-envoy-internal": "true",
            "x-envoy-downstream-service-cluster": "test-service",
        },
    )

    assert response.status_code == 200
    mock_get_team.assert_called_once_with("T00000000")


def test_non_enterprise_install_team_id(
    client,
    mock_get_team,
    mock_get_bot,
    mock_auth_checks,
):
    """Test team ID lookup prioritizes root team.id for non-enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = False
    payload["team"] = {"id": "T00000000"}
    payload["original_message"]["team"] = "T11111111"
    payload["user"]["team_id"] = "T22222222"

    response = client.post(
        "/api/v1/slack/interactive",
        data={"payload": json.dumps(payload)},
        headers={
            "x-envoy-internal": "true",
            "x-envoy-downstream-service-cluster": "test-service",
        },
    )

    assert response.status_code == 200
    mock_get_team.assert_called_once_with("T00000000")


def test_non_enterprise_install_original_message_fallback(
    client,
    mock_get_team,
    mock_get_bot,
    mock_auth_checks,
):
    """Test team ID lookup falls back to original_message.team for non-enterprise installs"""
    payload = load_test_payload()
    logger.debug("Original payload: %s", json.dumps(payload, indent=2))

    payload["is_enterprise_install"] = False
    payload["team"] = None
    payload["original_message"]["team"] = "T00000000"
    payload["user"]["team_id"] = "T11111111"

    logger.debug("Modified payload: %s", json.dumps(payload, indent=2))

    form_data = {"payload": json.dumps(payload)}
    logger.debug("Form data being sent: %s", form_data)

    response = client.post(
        "/api/v1/slack/interactive",
        data=form_data,
        headers={
            "x-envoy-internal": "true",
            "x-envoy-downstream-service-cluster": "test-service",
        },
    )

    logger.debug("Response status: %d", response.status_code)
    logger.debug("Response data: %s", response.get_json())

    assert response.status_code == 200
    mock_get_team.assert_called_once_with("T00000000")


def test_missing_team_id(client, mock_get_team, mock_get_bot, mock_auth_checks):
    """Test error handling when no team ID can be found"""
    payload = load_test_payload()
    payload["team"] = None
    payload["original_message"]["team"] = None
    payload["user"]["team_id"] = None

    response = client.post(
        "/api/v1/slack/interactive",
        data={"payload": json.dumps(payload)},
        headers={
            "x-envoy-internal": "true",
            "x-envoy-downstream-service-cluster": "test-service",
        },
    )

    assert response.status_code == 403
    assert "No team id found in interactive component" in response.get_json()["error"]
