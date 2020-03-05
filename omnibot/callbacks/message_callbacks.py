"""
Message callbacks for internal omnibot functionality.
"""

import json
import logging
import random

from omnibot.services.slack.team import Team
from omnibot.services.slack.bot import Bot

logger = logging.getLogger(__name__)


def help_callback(container):
    """
    Callback for omnibot help info.
    """
    payload = container.payload
    logger.debug('Help callback text: {}'.format(payload['text']))
    logger.debug('Help callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    ret_action = {
        'action': 'chat.postMessage',
        'kwargs': {'attachments': []}
    }
    ret = {'actions': [ret_action]}
    command_fields = []
    regex_fields = []
    team = Team.get_team_by_name(payload['team']['name'])
    bot = Bot.get_bot_by_name(team, payload['bot']['name'])
    for handler in bot.message_handlers:
        if handler['match_type'] == 'command':
            command_fields.append({
                'title': handler['match'],
                'value': handler.get('description', ''),
                'short': False
            })
        if handler['match_type'] == 'regex':
            regex_fields.append({
                'title': handler['match'],
                'value': handler.get('description', ''),
                'short': False
            })
    if command_fields:
        ret_action['kwargs']['attachments'].append({
            'title': 'Commands:',
            'fields': command_fields
        })
    if regex_fields:
        ret_action['kwargs']['attachments'].append({
            'title': 'Regex matches:',
            'fields': regex_fields
        })
    return ret


def specials_callback(container, channels):
    """
    A specials callback that checks for @here or @channel
    and asks the sender to not use the specials.
    """
    payload = container.payload
    logger.debug('Specials callback text: {}'.format(payload['text']))
    logger.debug('Specials callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )

    fallback_text = "Please don't use {special}"

    config_for_channel = channels.get(payload['channel']["name_normalized"])

    if not config_for_channel:
        return {}

    for special in ['@here', '@channel']:
        if special in payload['specials'].values():
            text = config_for_channel.get('message', fallback_text)
            try:
                text = text.format(
                    special=special,
                    member_count=payload['channel'].get('num_members', '`?`')
                )
            except KeyError:
                logger.error(
                    "Misconfigured message string for {}".format(
                        payload['channel']["name_normalized"]
                    )
                )
                text = fallback_text.format(special=special)

            actions = [
                {
                    'action': 'chat.postMessage',
                    'kwargs': {'text': text}
                }
            ]

            if config_for_channel.get('reaction'):
                actions.append({
                    'action': 'reactions.add',
                    'kwargs': {
                        'name': config_for_channel.get('reaction'),
                        'timestamp': payload['ts'],
                        'channel': payload['channel_id']
                    }
                })

            return {'actions': actions}
    return {}


def channel_channel_callback(container):
    payload = container.payload
    logger.debug('Channel channel callback text: {}'.format(payload['text']))
    logger.debug(
        'Channel channel callback payload: {}'.format(
            json.dumps(payload, indent=2)
        )
    )

    if payload['channel']['name_normalized'] != 'channel-channel':
        return {}

    return {
        'actions': [
            {
                'action': 'reactions.add',
                'kwargs': {
                    'name': 'please_make_sure_to_use_at_here_or_at_channel_in_your_message_next_time',  # noqa: E501
                    'timestamp': payload['ts'],
                    'channel': payload['channel_id']
                }
            },
            {
                'action': 'reactions.add',
                'kwargs': {
                    'name': 'mega',
                    'timestamp': payload['ts'],
                    'channel': payload['channel_id']
                }
            },
            {
                'action': 'reactions.add',
                'kwargs': {
                    'name': 'bangbang',
                    'timestamp': payload['ts'],
                    'channel': payload['channel_id']
                }
            },
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'thread_ts': None,
                    'text': 'Please make sure to use <!here> or <!channel> in your message next time.',  # noqa: E501
                },
            },
        ],
    }


def congratulations_bot_callback(container, channels, emojis, messages):
    payload = container.payload
    logger.debug('Congratulations bot\'s callback text: {}'.format(payload['text']))
    logger.debug(
        'Congratulations bot\'s callback payload: {}'.format(
            json.dumps(payload, indent=2)
        )
    )

    if payload['channel']['name'] not in channels:
        return {}

    return {
        'actions': [
            {
                'action': 'reactions.add',
                'kwargs': {
                    'name': random.choice(emojis),
                    'timestamp': payload['ts'],
                    'channel': payload['channel_id']
                }
            },
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'thread_ts': payload['ts'],
                    'text': random.choice(messages),
                },
            },
        ],
    }


def channel_response_callback(container, channels):
    """
    A callback to give back a canned response for regex matches in channels
    """
    payload = container.payload
    logger.debug('channel response callback text: {}'.format(payload['text']))
    logger.debug('channel response payload: {}'.format(
        json.dumps(payload, indent=2))
    )

    config_for_channel = channels.get(payload['channel']["name_normalized"])

    if not config_for_channel:
        return {}

    try:
        find_list = config_for_channel['find']
    except KeyError:
        logger.error(
            'Missing find in channel_response_callback for {}'.format(
                payload['channel']["name_normalized"]
            )
        )
        return {}

    matched = False
    # Match entire words if this is a single word, to be less greedy
    for find in find_list:
        if ' ' not in find:
            matched = find in payload['parsed_text'].split()
        else:
            matched = find in payload['parsed_text']
        if matched:
            break
    if not matched:
        return {}

    try:
        text = config_for_channel['message']
    except KeyError:
        logger.error(
            'Missing message in channel_response_callback for {}'.format(
                payload['channel']["name_normalized"]
            )
        )
        return {}

    actions = [
        {
            'action': 'chat.postMessage',
            'kwargs': {'text': text}
        }
    ]

    return {'actions': actions}


def example_topic_callback(container):
    """
    A callback for setting the topic
    """
    payload = container.payload
    logger.debug('Example topic callback text: {}'.format(payload['text']))
    logger.debug('Example topic callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    return {
        'actions':
        [
            {
                'action': 'channels.setTopic',
                'kwargs': {
                    'topic': payload['args'],
                    'channel': payload['channel_id']
                }
            }
        ]
    }


def example_attachment_callback(container):
    """
    A callback for responding with an attachment
    """
    payload = container.payload
    logger.debug('Example attachment callback text: {}'.format(payload['text']))
    logger.debug('Example attachment callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    return {
        'actions':
        [
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'thread': False,
                    'attachments': [{
                        'fallback': 'Example attachment!',
                        'color': '#36a64f',
                        'fields': [{
                            'title': 'Hello',
                            'value': 'World'
                        }]
                    }]
                }
            }
        ]
    }


def test_callback(container, text=''):
    """
    A callback used for basic testing.
    """
    return {
        'actions':
        [
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'text': '{}'.format(text)
                }
            }
        ]
    }
