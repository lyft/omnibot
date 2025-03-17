import json
import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from omnibot.routes.api import slack_interactive_component
from omnibot.services.slack.bot import Bot
from omnibot.services.slack.team import Team

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(TESTS_DIR)),
    "data",
    "mock",
    "interactive",
)


def load_test_payload(filename="interactive_enterprise.json"):
    with open(os.path.join(MOCK_DIR, filename)) as f:
        return json.load(f)


@pytest.fixture
def mock_team():
    team = MagicMock(spec=Team)
    team.team_id = "T00000000"
    return team


@pytest.fixture
def mock_bot():
    bot = MagicMock(spec=Bot)
    bot.verification_token = "test_token_123"
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


def test_enterprise_install_original_message_team(mock_get_team, mock_get_bot):
    """Test team ID lookup prioritizes original_message.team for enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = True
    payload["team"] = None
    payload["original_message"]["team"] = "T00000000"
    payload["user"]["team_id"] = "T11111111"

    with patch("flask.request") as mock_request:
        mock_request.form.to_dict.return_value = {"payload": json.dumps(payload)}
        response = slack_interactive_component()
        assert response[1] == 200
        mock_get_team.assert_called_once_with("T00000000")


def test_enterprise_install_user_team_id_fallback(mock_get_team, mock_get_bot):
    """Test team ID lookup falls back to user.team_id for enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = True
    payload["team"] = None
    payload["original_message"]["team"] = None
    payload["user"]["team_id"] = "T00000000"

    with patch("flask.request") as mock_request:
        mock_request.form.to_dict.return_value = {"payload": json.dumps(payload)}
        response = slack_interactive_component()
        assert response[1] == 200
        mock_get_team.assert_called_once_with("T00000000")


def test_non_enterprise_install_team_id(mock_get_team, mock_get_bot):
    """Test team ID lookup prioritizes root team.id for non-enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = False
    payload["team"] = {"id": "T00000000"}
    payload["original_message"]["team"] = "T11111111"
    payload["user"]["team_id"] = "T22222222"

    with patch("flask.request") as mock_request:
        mock_request.form.to_dict.return_value = {"payload": json.dumps(payload)}
        response = slack_interactive_component()
        assert response[1] == 200
        mock_get_team.assert_called_once_with("T00000000")


def test_non_enterprise_install_original_message_fallback(mock_get_team, mock_get_bot):
    """Test team ID lookup falls back to original_message.team for non-enterprise installs"""
    payload = load_test_payload()
    payload["is_enterprise_install"] = False
    payload["team"] = None
    payload["original_message"]["team"] = "T00000000"
    payload["user"]["team_id"] = "T11111111"

    with patch("flask.request") as mock_request:
        mock_request.form.to_dict.return_value = {"payload": json.dumps(payload)}
        response = slack_interactive_component()
        assert response[1] == 200
        mock_get_team.assert_called_once_with("T00000000")


def test_missing_team_id(mock_get_team, mock_get_bot):
    """Test error handling when no team ID can be found"""
    payload = load_test_payload()
    payload["team"] = None
    payload["original_message"]["team"] = None
    payload["user"]["team_id"] = None

    with patch("flask.request") as mock_request:
        mock_request.form.to_dict.return_value = {"payload": json.dumps(payload)}
        response = slack_interactive_component()
        assert response[1] == 403
        assert (
            "No team id found in interactive component"
            in response[0].get_json()["error"]
        )
