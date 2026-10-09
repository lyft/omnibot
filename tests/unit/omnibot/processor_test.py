from omnibot import processor
from omnibot.services.slack.bot import Bot
from omnibot.services.slack.team import Team


def test_slackbot_message_only_matches_opted_in_handlers(mocker):
    _team = Team.get_team_by_name("testteam")
    _bot = Bot.get_bot_by_name(_team, "echobot")
    slackbot_handler = {
        "match_type": "regex",
        "match": "",
        "match_slackbot": True,
        "callbacks": [{"module": "slackbot"}],
    }
    other_handler = {
        "match_type": "regex",
        "match": "",
        "callbacks": [{"module": "other"}],
    }
    _bot._message_handlers = [slackbot_handler, other_handler]
    message = mocker.Mock(
        bot=_bot,
        thread_ts=None,
        from_slackbot=True,
        parsed_text="Reminder: run the report.",
    )
    callback_mock = mocker.patch("omnibot.processor._handle_message_callback")
    processor._process_message_message_handlers(message)
    callback_mock.assert_called_once_with(message, {"module": "slackbot"})
