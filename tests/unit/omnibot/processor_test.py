from copy import deepcopy

import pytest

from omnibot import processor
from omnibot.services.slack.message import Message


@pytest.mark.parametrize(
    "forward_flags",
    [[True, False, True], [False, True, False], [None, "true", 1]],
)
@pytest.mark.parametrize("matched", [False, True])
@pytest.mark.parametrize("headers", [None, {"X-Existing": "keep"}])
def test_action_token_header_is_isolated_to_each_handler(
    forward_flags,
    matched,
    headers,
    mocker,
):
    log = mocker.patch.object(processor.logger, "info")
    mocker.patch("omnibot.services.slack.get_user", return_value={})
    mocker.patch("omnibot.services.slack.get_channel", return_value={})
    mocker.patch.object(Message, "_parse_payload")
    http = mocker.patch(
        "omnibot.callbacks.network_callbacks._get_requests_session",
    ).return_value
    http.post.return_value.status_code = 200
    http.post.return_value.json.return_value = {}
    callback = {
        "module": "omnibot.callbacks.network_callbacks:http_callback",
        "kwargs": {
            "request_kwargs": {
                "url": "https://example.com/callback",
                "headers": headers,
            },
        },
    }
    bot = mocker.Mock()
    bot.message_handlers = [
        {
            "match": "test" if matched else "does-not-match",
            "match_type": "regex",
            "forward_action_token": flag,
            "callbacks": [callback, callback],
        }
        for flag in forward_flags
    ]
    original_handlers = deepcopy(bot.message_handlers)
    mocker.patch.object(processor.settings, "HELP_CALLBACK", {"callback": callback})
    event = {
        "type": "app_mention",
        "text": "test",
        "ts": "1234567.000001",
        "channel": "C123456AB",
    }
    message = Message(bot, event, {})
    message._payload["directed"] = True
    expected_flags = (
        [flag for flag in forward_flags for _ in range(2)] if matched else [False]
    )
    for token in ("synthetic-action-token", "next-synthetic-action-token", None):
        if token:
            event["action_token"] = token
        else:
            event.pop("action_token", None)
        original_event = deepcopy(event)
        http.post.reset_mock()

        processor._process_message_message_handlers(message)

        assert http.post.call_count == len(expected_flags)
        for call, flag in zip(http.post.call_args_list, expected_flags):
            expected_headers = headers
            if flag is True and token:
                expected_headers = {**(headers or {}), "X-Slack-Action-Token": token}
            assert call.kwargs["headers"] == expected_headers
            assert "action_token" not in call.kwargs["json"]
        assert not hasattr(message, "action_token")
        assert "action_token" not in message.payload
        assert event == original_event
        assert bot.message_handlers == original_handlers
    assert "synthetic-action-token" not in repr(log.call_args_list)
