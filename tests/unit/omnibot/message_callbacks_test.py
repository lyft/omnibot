import json
from copy import deepcopy

import pytest

from omnibot.callbacks import message_callbacks


@pytest.mark.parametrize("include_action_token", [False, True])
@pytest.mark.parametrize(
    "callback_name, kwargs, log_prefix",
    [
        ("help_callback", {}, "Help callback"),
        ("specials_callback", {"channels": {}}, "Specials callback"),
        ("channel_channel_callback", {}, "Channel channel callback"),
        (
            "congratulations_bot_callback",
            {"channels": [], "emojis": [], "messages": []},
            "Congratulations bot's callback",
        ),
        ("channel_response_callback", {"channels": {}}, "channel response"),
        ("example_topic_callback", {}, "Example topic callback"),
        ("example_attachment_callback", {}, "Example attachment callback"),
    ],
)
def test_callback_logs_payload_without_action_token(
    callback_name,
    kwargs,
    log_prefix,
    include_action_token,
    mocker,
    caplog,
):
    payload = {
        "text": "test message",
        "team": {"name": "testteam"},
        "bot": {"name": "echobot"},
        "channel": {"name": "test-channel", "name_normalized": "test-channel"},
        "channel_id": "C123456AB",
        "args": "test topic",
    }
    expected_log = f"{log_prefix} payload: {json.dumps(payload, indent=2)}"
    action_token = "synthetic-action-token-do-not-log"
    if include_action_token:
        payload["action_token"] = action_token
    original_payload = deepcopy(payload)
    container = mocker.Mock(payload=payload)
    mocker.patch.object(message_callbacks.Team, "get_team_by_name")
    mocker.patch.object(
        message_callbacks.Bot,
        "get_bot_by_name",
        return_value=mocker.Mock(message_handlers=[]),
    )
    caplog.set_level("DEBUG")

    getattr(message_callbacks, callback_name)(container, **kwargs)

    assert expected_log in caplog.messages
    assert action_token not in caplog.text
    assert "action_token" not in caplog.text
    assert container.payload == original_payload
