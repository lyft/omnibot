"""
Core processing logic.
"""
import importlib
import json
import re
from typing import Any
from typing import Mapping

import requests

from omnibot import logging
from omnibot import settings
from omnibot.services import slack
from omnibot.services import stats
from omnibot.services.slack import get_bot_info
from omnibot.services.slack import get_message
from omnibot.services.slack import parser
from omnibot.services.slack.base_message import BaseMessage
from omnibot.services.slack.bot import Bot
from omnibot.services.slack.interactive_component import InteractiveComponent
from omnibot.services.slack.message import Message
from omnibot.services.slack.message import MessageUnsupportedError
from omnibot.services.slack.reaction import Reaction
from omnibot.services.slack.reaction import ReactionUnsupportedError
from omnibot.services.slack.slash_command import SlashCommand
from omnibot.services.slack.team import Team
from omnibot.utils import get_callback_id
from omnibot.utils import merge_logging_context

logger = logging.getLogger(__name__)


def process_event(event):
    """
    Dispatcher for slack api events.
    """
    statsd = stats.get_statsd_client()
    team = Team.get_team_by_id(event["team_id"])
    bot = Bot.get_bot_by_bot_id(team, event["api_app_id"])
    event_info = event["event"]
    event_type = event_info["type"]
    event_trace = merge_logging_context(
        {
            "event_ts": event_info["event_ts"],
            "event_type": event_type,
        },
        bot.logging_context,
    )
    statsd.incr(f"event.process.attempt.{event_type}")
    if event_type == "message" or event_type == "app_mention":
        _process_message_event(bot, event_info, event_trace, event_type)
    elif event_type == "reaction_added" or event_type == "reaction_removed":
        _process_reaction_event(bot, event_info, event_trace, event_type)
    else:
        logger.debug("Event is not a message or reaction type.", extra=event_trace)
        logger.debug(event)


def _process_message_event(bot, event_info, event_trace, event_type):
    """
    Process message or app_mention events.
    """
    statsd = stats.get_statsd_client()
    try:
        with statsd.timer("process_event"):
            logger.debug(
                f"Processing event: {json.dumps(event_info, indent=2)}",
                extra=event_trace,
            )
            try:
                message = Message(bot, event_info, event_trace)
                _process_message_message_handlers(message)
            except MessageUnsupportedError:
                pass
    except Exception:
        statsd.incr(f"event.process.failed.{event_type}")
        logger.exception(
            "Could not process message event.",
            exc_info=True,
            extra=event_trace,
        )


def _process_reaction_event(bot, event_info, event_trace, event_type):
    """
    Process reaction_added or reaction_removed events.
    """
    statsd = stats.get_statsd_client()
    try:
        with statsd.timer("process_event"):
            logger.debug(
                f"Processing event: {json.dumps(event_info, indent=2)}",
                extra=event_trace,
            )
            try:
                reaction = Reaction(bot, event_info, event_trace)
                _process_reaction_message_handlers(reaction)
            except ReactionUnsupportedError:
                pass
    except Exception:
        statsd.incr(f"event.process.failed.{event_type}")
        logger.exception(
            "Could not process reaction event.",
            exc_info=True,
            extra=event_trace,
        )


def _process_message_message_handlers(message: Message):
    bot = message.bot
    statsd = stats.get_statsd_client()
    command_matched = False
    handler_called = False
    for handler in bot.message_handlers:
        # We only match commands against directed messages
        if handler["match_type"] == "command":
            if not _should_handle_command(handler, message):
                continue
            # We only match against a single command
            if command_matched:
                continue
            if message.command_text.startswith(handler["match"]):
                command_matched = True
                message.set_match("command", handler["match"])
                for callback in handler["callbacks"]:
                    _handle_message_callback(message, callback)
                    handler_called = True
        if handler["match_type"] == "regex":
            match = bool(re.search(handler["match"], message.parsed_text))
            regex_should_not_match = handler.get("regex_type") == "absence"
            # A matched regex should callback only if the regex is supposed to
            # match. An unmatched regex should callback only if the regex is
            # not supposed to match.
            if match != regex_should_not_match:
                message.set_match("regex", handler["match"])
                for callback in handler["callbacks"]:
                    _handle_message_callback(message, callback)
                    handler_called = True
    if handler_called:
        statsd.incr("event.handled")
    elif not handler_called:
        _handle_help(message)


def _process_reaction_message_handlers(reaction: Reaction):
    bot = reaction.bot
    statsd = stats.get_statsd_client()
    handler_called = False
    item_channel = reaction.item_channel
    item_ts = reaction.item_ts
    item_user = reaction.item_user

    if item_user:
        # Reaction is on a thread reply
        if item_user != bot.user_id:
            statsd.incr("event.ignored")
            return
    elif not _is_message_from_bot(bot, item_channel, item_ts):
        statsd.incr("event.ignored")
        return

    for handler in bot.message_handlers:
        if handler.get("match_type") == "reaction":
            match = bool(re.fullmatch(handler["match"], reaction.emoji_name))
            regex_should_not_match = handler.get("regex_type") == "absence"
            # A matched regex should callback only if the regex is supposed to
            # match. An unmatched regex should callback only if the regex is
            # not supposed to match.
            if match != regex_should_not_match:
                reaction.set_match("reaction", handler["match"])
                for callback in handler["callbacks"]:
                    _handle_message_callback(reaction, callback)
                    handler_called = True

    if handler_called:
        statsd.incr("event.handled")
    elif not handler_called:
        logger.debug("no handler found")
        statsd.incr("event.ignored")


def _is_message_from_bot(bot: Bot, channel: str, ts: str):
    """
    Some events, like reactions, do not have all the ids we need to determine who wrote the message.
    """
    message = get_message(bot, channel, ts)
    if not message:
        logger.warning("Failed to retrieve valid message")
        return False
    elif "bot_id" not in message:
        logger.debug("Message is not from a bot")
        return False
    # There can be multiple bot_ids for the same bot
    bot_info = get_bot_info(bot, message["bot_id"])
    if not bot_info or bot_info["app_id"] != bot.bot_id:
        logger.debug("Reaction is not on a message from this bot")
        return False
    return True


def process_slash_command(command):
    """
    Dispatcher for slack slash commands.
    """
    statsd = stats.get_statsd_client()
    team = Team.get_team_by_id(command["team_id"])
    bot = Bot.get_bot_by_bot_id(team, command["omnibot_bot_id"])
    if command["command"].startswith("/"):
        command_name = command["command"][1:]
    else:
        command_name = command["command"]
    event_trace = merge_logging_context(
        {
            "trigger_id": command["trigger_id"],
            "command": command_name,
        },
        bot.logging_context,
    )
    statsd.incr(f"slash_command.process.attempt.{command_name}")
    try:
        with statsd.timer("process_slash_command"):
            logger.debug(
                f"Processing slash_command: {json.dumps(command, indent=2)}",
                extra=event_trace,
            )
            slash_command = SlashCommand(bot, command, event_trace)
            _process_slash_command_handlers(slash_command)
    except Exception:
        statsd.incr(f"slash_command.process.failed.{command_name}")
        logger.exception(
            "Could not process slash command.",
            exc_info=True,
            extra=event_trace,
        )


def process_interactive_component(component):
    """
    Dispatcher for slack interactive components
    """
    statsd = stats.get_statsd_client()
    team = Team.get_team_by_id(component["team"]["id"])
    bot = Bot.get_bot_by_bot_id(team, component["omnibot_bot_id"])
    event_trace = merge_logging_context(
        {
            "callback_id": get_callback_id(component),
            "component_type": component["type"],
        },
        bot.logging_context,
    )
    statsd.incr(
        f"interactive_component.process.attempt.{get_callback_id(component)}",
    )
    try:
        with statsd.timer("process_interactive_component"):
            logger.debug(
                "Processing interactive component: {}".format(
                    json.dumps(component, indent=2),
                ),
                extra=event_trace,
            )
            interactive_component = InteractiveComponent(bot, component, event_trace)
            _process_interactive_component(interactive_component)
    except Exception:
        statsd.incr(
            "interactive_component.process.failed.{}".format(
                get_callback_id(component),
            ),
        )
        logger.exception(
            "Could not process interactive component.",
            exc_info=True,
            extra=event_trace,
        )


def _process_slash_command_handlers(command):
    handler_called = False
    for handler in command.bot.slash_command_handlers:
        if command.command != handler.get("command"):
            continue
        for callback in handler["callbacks"]:
            _handle_slash_command_callback(
                command,
                callback,
                handler.get("response_type", "ephemeral"),
            )
            handler_called = True
    if not handler_called:
        # TODO: send back a default help message here.
        pass


def _process_interactive_component(component):
    handler_called = False
    for handler in component.bot.interactive_component_handlers:
        if component.callback_id != handler.get("callback_id"):
            continue
        for callback in handler.get("callbacks", []):
            _handle_interactive_component_callback(
                component,
                callback,
                handler.get("response_type", "ephemeral"),
            )
            handler_called = True
    if not handler_called:
        # TODO: send back a default help message here.
        pass


def _handle_help(message):
    statsd = stats.get_statsd_client()
    if message.directed:
        statsd.incr("event.defaulted")
        if settings.HELP_CALLBACK:
            _handle_message_callback(message, settings.HELP_CALLBACK["callback"])
        elif settings.DEFAULT_TO_HELP:
            _handle_message_callback(
                message,
                {"module": "omnibot.callbacks.message_callbacks:help_callback"},
            )
        else:
            # TODO: respond with error message here
            pass
    else:
        statsd.incr("event.ignored")


def _should_handle_command(handler, message):
    handle_mention = handler.get("match_mention", False) and message.mentioned
    if message.directed or handle_mention:
        return True
    else:
        return False


def parse_kwargs(kwargs, bot, event_trace=None):
    if event_trace is None:
        event_trace = {}
    statsd = stats.get_statsd_client()
    omnibot_parse = kwargs.pop("omnibot_parse", {})
    for attr, to_parse in omnibot_parse.items():
        if attr not in kwargs:
            logger.warning(
                f"{attr} not found in kwargs when parsing post response.",
                extra=event_trace,
            )
        with statsd.timer("unexpand_metadata"):
            if "specials" in to_parse:
                kwargs[attr] = parser.unextract_specials(kwargs[attr])
            if "channels" in to_parse:
                kwargs[attr] = parser.unextract_channels(kwargs[attr], bot)
            if "users" in to_parse:
                kwargs[attr] = parser.unextract_users(kwargs[attr], bot)


def _handle_post_message(message: BaseMessage, kwargs):
    try:
        channel = kwargs.pop("channel")
    except KeyError:
        channel = message.channel_id
    try:
        thread_ts = kwargs.pop("thread_ts")
    except KeyError:
        if message.channel.get("is_im"):
            thread_ts = None
        else:
            thread_ts = message.ts
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    parse_kwargs(kwargs, message.bot, message.event_trace)
    try:
        ret = slack.client(
            message.bot,
        ).api_call("chat.postMessage", channel=channel, **kwargs)
    except json.decoder.JSONDecodeError:
        logger.exception(
            f"JSON decode failure when parsing {kwargs}",
            extra=message.event_trace,
        )
        return
    logger.debug(ret, extra=message.event_trace)
    if not ret["ok"]:
        logger.error(ret, extra=message.event_trace)


def _handle_action(action, container, kwargs):
    parse_kwargs(kwargs, container.bot, container.event_trace)
    ret = slack.client(
        container.bot,
    ).api_call(action, **kwargs)
    logger.debug(
        f"return from action {action}: {ret}",
        extra=container.event_trace,
    )
    if not ret["ok"]:
        if ret.get("error") == "missing_scope":
            logger.warning(
                f"action {action} failed, attempting as user.",
                extra=container.event_trace,
            )
            try:
                ret = slack.client(container.bot, client_type="user").api_call(
                    action,
                    **kwargs,
                )
            except json.decoder.JSONDecodeError:
                logger.exception(
                    f"JSON decode failure when parsing {kwargs}",
                    extra=container.event_trace,
                )
                return
            logger.debug(
                f"return from action {action}: {ret}",
                extra=container.event_trace,
            )
            if not ret["ok"]:
                logger.debug(
                    f"return from failed action {action}: {ret}",
                    extra=container.event_trace,
                )
        else:
            if not ret["ok"]:
                logger.debug(
                    f"return from failed action {action}: {ret}",
                    extra=container.event_trace,
                )


def _handle_message_callback(message: BaseMessage, callback: Mapping[str, Any]):
    logger.info(
        'Handling callback for message: match_type="{}" match="{}"'.format(
            message.match_type,
            message.match,
        ),
        extra={
            **message.event_trace,
            "module": callback["module"],
            "request_kwargs": callback.get("kwargs", {}).get("request_kwargs", {}),
            "client_kwargs": {
                "service": callback.get("kwargs", {})
                .get("client_kwargs", {})
                .get("service", ""),
            },
        },
    )
    response = _handle_callback(message, callback)
    for action in response.get("actions", []):
        if not isinstance(action, dict):
            logger.error("Action in response is not a dict.", extra=message.event_trace)
            continue
        logger.debug(
            f"action for callback: {action}",
            extra=message.event_trace,
        )
        if action["action"] == "chat.postMessage":
            _handle_post_message(message, action["kwargs"])
        else:
            _handle_action(action["action"], message, action["kwargs"])


def _handle_slash_command_callback(command, callback, response_type):
    logger.info(
        f'Handling callback for slash_command: command="{command.command}"',
        extra={**command.event_trace, "callback": callback},
    )
    response = _handle_callback(command, callback)
    for command_response in response.get("responses", []):
        logger.debug(
            "Handling response for callback (pre-parse): {}".format(
                json.dumps(command_response),
            ),
            extra=command.event_trace,
        )
        if "response_type" not in command_response:
            command_response["response_type"] = response_type
        parse_kwargs(command_response, command.bot, command.event_trace)
        logger.debug(
            "Handling response for callback (post-parse): {}".format(
                json.dumps(command_response),
            ),
            extra=command.event_trace,
        )
        r = requests.post(command.response_url, json=command_response)
        if r.status_code != requests.codes.ok:
            msg = "Got status code {0} for {1}, with response: {2}"
            logger.error(
                msg.format(r.status_code, command.response_url, r.text),
                extra=command.event_trace,
            )
    for action in response.get("actions", []):
        if not isinstance(action, dict):
            logger.error("Action in response is not a dict.", extra=command.event_trace)
            continue
        logger.debug(
            f"Action in response: {action}",
            extra=command.event_trace,
        )
        _handle_action(action["action"], command, action["kwargs"])


def _handle_interactive_component_callback(component, callback, response_type):
    logger.info(
        "Handling callback for interactive component",
        extra={**component.event_trace, "callback": callback},
    )
    response = _handle_callback(component, callback)
    if response_type == "raw":
        return response
    for component_response in response.get("responses", []):
        logger.debug(
            "Handling response for callback (pre-parse): {}".format(
                json.dumps(component_response),
            ),
            extra=component.event_trace,
        )
        if "response_type" not in component_response:
            component_response["response_type"] = response_type
        parse_kwargs(component_response, component.bot, component.event_trace)
        logger.debug(
            "Handling response for callback (post-parse): {}".format(
                json.dumps(component_response),
            ),
            extra=component.event_trace,
        )
        r = requests.post(component.response_url, json=component_response)
        if r.status_code != requests.codes.ok:
            msg = "Got status code {0} for {1}, with response: {2}"
            logger.error(
                msg.format(r.status_code, component.response_url, r.text),
                extra=component.event_trace,
            )
    for action in response.get("actions", []):
        if not isinstance(action, dict):
            logger.error(
                "Action in response is not a dict.",
                extra=component.event_trace,
            )
            continue
        logger.debug(
            f"Action in response: {action}",
            extra=component.event_trace,
        )
        if action["action"] == "chat.postMessage":
            _handle_post_message(component, action["kwargs"])
        else:
            _handle_action(action["action"], component, action["kwargs"])


def _handle_callback(container, callback):
    module_name, function_name = callback["module"].split(":")
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    kwargs = callback.get("kwargs", {})
    response = function(container=container, **kwargs)
    return response
