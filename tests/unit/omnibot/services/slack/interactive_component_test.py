from omnibot.services.slack.bot import Bot
from omnibot.services.slack.interactive_component import InteractiveComponent
from omnibot.services.slack.team import Team


def test_interactive_component(mocker):
    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_name(_team, "echobot")
    component = {
        "type": "message_action",
        "callback_id": "echobot_action_test",
        "action_ts": "1234567.12",
        "trigger_id": "376604117319.165116859648.515402022613c2893a80d6268c463e54",  # noqa:E501
        "response_url": "https://hooks.slack.com/app/T999999/375455994771/iMW9hNKFI739hGOw9FCXMlf4",  # noqa:E501
        "user": {"id": "A12345678", "name": "echobot"},
        "team": {"id": "T999999", "domain": "omnibot-test-domain"},
        "channel": {"id": "C123456AB", "name": "channel-channel"},
        "message": {
            "type": "message",
            "user": "A12345678",
            "text": "<@A12345678> echo I am <!here|here> in <#C123456AB|channel-channel>. See: <http://example.com> :simple_smile:",  # noqa:E501
            "ts": "1230000.00",
        },
    }
    event_trace = {
        "callback_id": "echobot_action_test",
        "app_id": _bot.bot_id,
        "team_id": _bot.team.team_id,
        "bot_receiver": _bot.name,
        "component_type": "message_action",
    }
    get_user_mock = mocker.patch("omnibot.services.slack.get_user")
    user_ret = {"A12345678": {}}
    get_user_mock.return_value = user_ret
    get_channel_mock = mocker.patch("omnibot.services.slack.get_channel")
    channel_ret = {"C123456AB": {}}
    get_channel_mock.return_value = channel_ret
    extract_users_mock = mocker.patch("omnibot.services.slack.parser.extract_users")
    users_ret = {"<@A12345678>": "echobot"}
    extract_users_mock.return_value = users_ret
    replace_users_mock = mocker.patch("omnibot.services.slack.parser.replace_users")
    replace_users_mock.return_value = "@echobot echo I am <!here|here> in <#C123456AB|channel-channel>. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_channels_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_channels"
    )
    channels_ret = {"<#C123456AB|channel-channel>": "channel-channel"}
    extract_channels_mock.return_value = channels_ret
    replace_channels_mock = mocker.patch(
        "omnibot.services.slack.parser.replace_channels"
    )
    replace_channels_mock.return_value = "@echobot echo I am <!here|here> in #channel-channel. See: <http://example.com> :simple_smile:"  # noqa:E501
    extract_subteams_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_subteams"
    )
    extract_subteams_mock.return_value = {}
    extract_specials_mock = mocker.patch(
        "omnibot.services.slack.parser.extract_specials"
    )
    special_ret = {"<!here|here>": "@here"}
    extract_specials_mock.return_value = special_ret
    replace_specials_mock = mocker.patch(
        "omnibot.services.slack.parser.replace_specials"
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
        "omnibot.services.slack.parser.extract_mentions"
    )
    extract_mentions_mock.return_value = True
    extract_command_mock = mocker.patch("omnibot.services.slack.parser.extract_command")
    extract_command_mock.return_value = "echo I am @here in #channel-channel. See: http://example.com :simple_smile:"  # noqa:E501
    _component = InteractiveComponent(_bot, component, event_trace)
    assert _component.event_trace == event_trace
    assert _component.bot == _bot
    assert _component.component_type == "message_action"
    assert _component.callback_id == "echobot_action_test"
    assert _component.action_ts == "1234567.12"
    assert (
        _component.trigger_id
        == "376604117319.165116859648.515402022613c2893a80d6268c463e54"
    )  # noqa:E501
    assert (
        _component.response_url
        == "https://hooks.slack.com/app/T999999/375455994771/iMW9hNKFI739hGOw9FCXMlf4"
    )  # noqa:E501
    assert _component.submission is None
    assert _component.channel["id"] == "C123456AB"
    assert _component.parsed_channel == channel_ret
    assert _component.user == component["user"]
    assert _component.team == {"name": _bot.team.name, "team_id": _bot.team.team_id}
    assert _component.message["parsed_user"] == user_ret
    assert _component.message["users"] == users_ret
    assert (
        _component.message["parsed_text"]
        == "@echobot echo I am @here in #channel-channel. See: http://example.com :simple_smile:"
    )  # noqa:E501
    assert _component.message.get("bot_id") is None
    assert _component.message["channels"] == channels_ret
    assert _component.message["specials"] == special_ret
    assert _component.message["emails"] == {}
    assert _component.message["urls"] == url_ret


def test_interactive_block_component(mocker):
    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_name(_team, "echobot")
    component = {
        "type": "block_actions",
        "response_url": "https://hooks.slack.com/app/T999999/375455994771/iMW9hNKFI739hGOw9FCXMlf4",  # noqa:E501
        "actions": [
            {"block_id": "echobot_action_test", "action_ts": "1561559117.130541"}
        ],
    }
    event_trace = {
        "callback_id": "echobot_action_test",
        "app_id": _bot.bot_id,
        "team_id": _bot.team.team_id,
        "bot_receiver": _bot.name,
        "component_type": "message_action",
    }
    _component = InteractiveComponent(_bot, component, event_trace)
    assert _component.callback_id == "echobot_action_test"
