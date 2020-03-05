"""
Slash command callbacks for internal omnibot functionality.
"""

import json
import logging

from omnibot.services.slack import get_emoji

logger = logging.getLogger(__name__)


def echo_callback(container):
    """
    Just respond back with whatever is sent in.
    """
    payload = container.payload
    logger.debug('echo callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    return {
        # Respond back to the slash command with the same text
        'responses': [
            {
                'text': payload['parsed_text'],
                'omnibot_parse': {
                    'text': ['users', 'specials', 'channels']
                }
            }
        ],
        # Post into the #echo channel, letting everyone @here know what's up
        'actions': [
            {
                'action': 'chat.postMessage',
                'kwargs': {
                    'channel': 'echo',
                    'text': '@here {}'.format(payload['parsed_text']),
                    'omnibot_parse': {
                        'channel': ['channels'],
                        'text': ['users', 'specials', 'channels']
                    }
                }
            }
        ]
    }


def tableflip_callback(container):
    """
    Respond back with a tableflip
    """
    payload = container.payload
    logger.debug('tableflip callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    return {
        # Respond back to the slash command with the same text
        'responses': [
            {
                'response_type': 'in_channel',
                'text': '(╯°□°)╯︵ ┻━┻'
            }
        ]
    }


def unfliptable_callback(container):
    """
    Respond back with an unfliptable
    """
    payload = container.payload
    logger.debug('unfliptable callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )
    return {
        # Respond back to the slash command with the same text
        'responses': [
            {
                'response_type': 'in_channel',
                'text': '┬─┬ノ( º _ ºノ)'
            }
        ]
    }


def bigemoji_callback(container):
    payload = container.payload
    logger.debug('bigemoji callback payload: {}'.format(
        json.dumps(payload, indent=2))
    )

    s = container.payload['text'].strip()
    args = s.split()

    if len(args) != 1:
        return {
            'responses': [
                {
                    'response_type': 'ephemeral',
                    'text': 'usage: /bigemoji :emoji:',
                }
            ]
        }
    else:
        emoji_name, = args
        emoji_name = emoji_name.strip(':')
        result = get_emoji(container.bot, emoji_name) or f':{emoji_name}:'
        resp = '<@{}> `/bigemoji :{}:` => {}'.format(
            container.payload["user_id"],  emoji_name, result,
        )

        return {
            'responses': [
                {
                    'response_type': 'in_channel',
                    'text': resp,
                    'omnibot_parse': {
                        'text': ['users', 'specials', 'channels']
                    }
                }
            ]
        }
