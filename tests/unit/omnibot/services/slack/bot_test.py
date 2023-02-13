import pytest

from omnibot.services.slack.bot import Bot
from omnibot.services.slack.bot import BotInitializationError
from omnibot.services.slack.team import Team


def test_team():
    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_name(_team, "echobot")
    assert _bot.name == "echobot"
    assert _bot.bot_id == "A12345678"
    assert _bot.team == _team
    assert _bot.oauth_user_token == "1234"
    assert _bot.oauth_bot_token == "1234"
    assert _bot.verification_token == "1234"

    _team = Team.get_team_by_id(team_id="TABCDEF12")
    _bot = Bot.get_bot_by_bot_id(_team, "A98765432")
    assert _bot.name == "echobot"
    assert _bot.bot_id == "A98765432"
    assert _bot.team == _team
    assert _bot.oauth_user_token == "1234"
    assert _bot.oauth_bot_token == ""
    assert _bot.verification_token == "1234"

    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_verification_token("5555")
    assert _bot.name == "pingbot"
    assert _bot.bot_id == "AABCDEF12"
    assert _bot.team == _team
    assert _bot.oauth_user_token == "5555"
    assert _bot.oauth_bot_token == "5555"
    assert _bot.verification_token == "5555"

    with pytest.raises(BotInitializationError):
        _bot = Bot.get_bot_by_name(_team, "fakebot")

    with pytest.raises(BotInitializationError):
        _bot = Bot.get_bot_by_bot_id(_team, "BADBOTID")
