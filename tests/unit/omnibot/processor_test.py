import pytest

from omnibot import processor
from omnibot.services.slack.message import Message


@pytest.mark.parametrize("forward_flags", [[True, False, True], [False, True, False]])
def test_action_token_is_isolated_to_each_handler(forward_flags, mocker):
    mocker.patch.object(processor.logger, "info")
    mocker.patch("omnibot.services.slack.get_user", return_value={})
    mocker.patch("omnibot.services.slack.get_channel", return_value={})
    mocker.patch.object(Message, "_parse_payload")
    bot = mocker.Mock()
    callback = {"module": "test:callback"}
    bot.message_handlers = [
        {
            "match": "test",
            "match_type": "regex",
            "forward_action_token": flag,
            "callbacks": [callback, callback],
        }
        for flag in forward_flags
    ]
    event = {
        "type": "app_mention",
        "text": "test",
        "ts": "1234567.000001",
        "channel": "C123456AB",
        "action_token": "synthetic-action-token",
    }
    message = Message(bot, event, {})
    payloads = []

    def receive(container, config):
        payloads.append(container.payload)
        return {}

    mocker.patch.object(processor, "_handle_callback", side_effect=receive)

    processor._process_message_message_handlers(message)

    assert len(payloads) == len(forward_flags) * 2
    for index, flag in enumerate(forward_flags):
        for payload in (payloads[index * 2], payloads[index * 2 + 1]):
            assert ("action_token" in payload) is flag
            if flag:
                assert payload["action_token"] == event["action_token"]
    assert "action_token" not in message.payload
    assert message.event == event
