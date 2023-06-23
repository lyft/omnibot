import copy

import pytest

from omnibot.services.slack.bot import Bot
from omnibot.services.slack.message import Message
from omnibot.services.slack.message import MessageUnsupportedError
from omnibot.services.slack.team import Team


def test_message(mocker):
    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_name(_team, "echobot")
    event = {
        "ts": "1234567.12",
        "thread_ts": None,
        "user": "A12345678",
        "text": "<@A12345678> echo I am <!here|here> in <#C123456AB|channel-channel>. See: <http://example.com> :simple_smile:",  # noqa:E501
        "channel": "C123456AB",
    }
    event_trace = {
        "event_ts": "1234567.12",
        "event_type": "message",
        "app_id": _bot.bot_id,
        "team_id": _bot.team.team_id,
        "bot_receiver": _bot.name,
    }
    get_user_mock = mocker.patch("omnibot.services.slack.get_user")
    user_ret = {"A12345678": {}}
    get_user_mock.return_value = user_ret
    get_channel_mock = mocker.patch("omnibot.services.slack.get_channel")
    channel_ret = {"C123456AB": {}}
    get_channel_mock.return_value = channel_ret
    extract_users_mock = mocker.patch("omnibot.services.slack.parser.extract_users")
    user_ret = {"<@A12345678>": "echobot"}
    extract_users_mock.return_value = user_ret
    replace_users_mock = mocker.patch("omnibot.services.slack.parser.replace_users")
    replace_users_mock.return_value = "@echobot echo I am <!here|here> in <#C123456AB|channel-channel>. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_channels_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_channels",
    )
    channels_ret = {"<#C123456AB|channel-channel>": "channel-channel"}
    extract_channels_mock.return_value = channels_ret
    replace_channels_mock = mocker.patch(
        "omnibot.services.slack.parser.replace_channels",
    )
    replace_channels_mock.return_value = "@echobot echo I am <!here|here> in #channel-channel. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_subteams_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_subteams",
    )
    extract_subteams_mock.return_value = {}
    extract_specials_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_specials",
    )
    special_ret = {"<!here|here>": "@here"}
    extract_specials_mock.return_value = special_ret
    replace_specials_mock = mocker.patch(
        "omnibot.services.slack.parser.replace_specials",
    )
    replace_specials_mock.return_value = "@echobot echo I am @here in #channel-channel. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_emojis_mock = mocker.patch("omnibot.services.slack.parser.extract_emojis")
    emoji_ret = {":simple-smile": "simple_smile"}
    extract_emojis_mock.return_value = emoji_ret
    extract_emails_mock = mocker.patch("omnibot.services.slack.parser.extract_emails")
    extract_emails_mock.return_value = {}
    replace_emails_mock = mocker.patch("omnibot.services.slack.parser.replace_emails")
    replace_emails_mock.return_value = "@echobot echo I am @here in #channel-channel. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_urls_mock = mocker.patch("omnibot.services.slack.parser.extract_urls")
    url_ret = {"<http://example.com>": "http://example.com"}
    extract_urls_mock.return_value = url_ret
    replace_urls_mock = mocker.patch("omnibot.services.slack.parser.replace_urls")
    replace_urls_mock.return_value = "@echobot echo I am @here in #channel-channel. See: http://example.com :simple_smile:"  # noqa:E501
    extract_mentions_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_mentions",
    )
    extract_mentions_mock.return_value = True
    extract_command_mock = mocker.patch("omnibot.services.slack.parser.extract_command")
    extract_command_mock.return_value = "echo I am @here in #channel-channel. See: http://example.com :simple_smile:"  # noqa:E501
    _message = Message(_bot, event, event_trace)
    assert _message.event == event
    assert _message.event_trace == event_trace
    assert _message.bot == _bot
    assert _message.subtype is None
    assert _message.text == event["text"]
    assert (
        _message.parsed_text
        == "@echobot echo I am @here in #channel-channel. See: http://example.com :simple_smile:"
    )  # noqa:E501
    assert (
        _message.command_text
        == "echo I am @here in #channel-channel. See: http://example.com :simple_smile:"
    )  # noqa:E501
    assert _message.directed is True
    assert _message.mentioned is True
    assert _message.channel_id == "C123456AB"
    assert _message.channel == channel_ret
    assert _message.user == event["user"]
    assert _message.ts == event["ts"]
    assert _message.thread_ts == event["thread_ts"]
    assert _message.team == {"name": _bot.team.name, "team_id": _bot.team.team_id}
    assert _message.bot_id is None
    assert _message.channels == channels_ret
    assert _message.users == user_ret
    assert _message.specials == special_ret
    assert _message.emails == {}
    assert _message.urls == url_ret
    assert _message.match_type is None
    assert _message.match is None
    assert _message.event_trace == event_trace
    _message.set_match("command", "echo")
    assert _message.match_type == "command"
    assert _message.match == "echo"
    assert _message.payload["command"] == "echo"
    assert (
        _message.payload["args"]
        == "I am @here in #channel-channel. See: http://example.com :simple_smile:"
    )  # noqa:E501
    _message.set_match("regex", None)
    assert _message.match_type == "regex"

    event_copy = copy.deepcopy(event)
    event_copy["bot_id"] = "A12345678"
    with pytest.raises(MessageUnsupportedError):
        _message = Message(_bot, event_copy, event_trace)

    event_copy = copy.deepcopy(event)
    event_copy["thread_ts"] = "1234568.00"
    with pytest.raises(MessageUnsupportedError):
        _message = Message(_bot, event_copy, event_trace)

    event_copy = copy.deepcopy(event)
    event_copy["subtype"] = "some_subtype"
    with pytest.raises(MessageUnsupportedError):
        _message = Message(_bot, event_copy, event_trace)
    
    event_copy = copy.deepcopy(event)
    event_copy["user"] = "USLACKBOT"
    with pytest.raises(MessageUnsupportedError):
        _message = Message(_bot, event_copy, event_trace)
