from __future__ import absolute_import

import logging
import yaml

from omnibot.utils.settings import bool_env, int_env, str_env

logger = logging.getLogger(__name__)

# Log config file used from any direct main entrypoint. You should
# use gunicorn config for the web worker.
LOG_CONFIG_FILE = str_env('LOG_CONFIG_FILE', '/etc/omnibot/logging.conf')

# Flask-related settings
DEBUG = bool_env('DEBUG', False)

# Config used for running wsgi directly, without gunicorn
HOST = str_env('HOST', '127.0.0.1')
PORT = int_env('PORT', 80)

# A statsd host
STATSD_HOST = str_env('STATSD_HOST', 'localhost')
# A statsd port
STATSD_PORT = int_env('STATSD_PORT', 8125)
# A statsd prefix for metrics
STATSD_PREFIX = str_env('STATSD_PREFIX', 'omnibot')

EXIT_ON_BAD_CONFIG = bool_env('EXIT_ON_BAD_CONFIG', True)
CONFIG_FILE = str_env('CONFIG_FILE', '/etc/omnibot/omnibot.conf')
try:
    with open(CONFIG_FILE) as _config_file:
        _config = yaml.load(_config_file)
except Exception:
    if EXIT_ON_BAD_CONFIG:
        raise
    logger.error(f'Failed to load configuration file: {CONFIG_FILE}')
    _config = {}

# authnz checks, permissions and bindings
AUTHORIZATION = _config.get('authorization', {})

# Slack bot data
PRIMARY_SLACK_BOT = _config.get('primary_bot', {})
if not PRIMARY_SLACK_BOT:
    logger.warning('primary_bot not set in configuration; watcher will not be able to refresh caches')
SLACK_TEAMS = _config.get('teams', {})
if not SLACK_TEAMS:
    message = 'teams not set in configuration; omnibot has no functionality without teams defined'
    if EXIT_ON_BAD_CONFIG:
        raise Exception(message)
    logger.warning(message)
SLACK_BOT_TOKENS = {}
for team, bots in _config.get('bots', {}).items():
    SLACK_BOT_TOKENS[team] = {}
    for bot_name, bot_id in bots.items():
        _v_token = str_env(
            'CREDENTIALS_SLACK_VERIFICATION_TOKEN_{}'.format(bot_id.upper())
        )
        _o_token = str_env(
            'CREDENTIALS_SLACK_OAUTH_TOKEN_{}'.format(bot_id.upper())
        )
        _o_bot_token = str_env(
            'CREDENTIALS_SLACK_OAUTH_BOT_TOKEN_{}'.format(bot_id.upper())
        )
        # We require a verification token, and require some type of
        # oauth token.
        if not _v_token:
            logger.warning(
                '{} bot missing verification token.'.format(bot_name)
            )
            continue
        if not _o_token and not _o_bot_token:
            logger.warning(
                '{} bot missing oauth tokens.'.format(bot_name)
            )
            continue
        SLACK_BOT_TOKENS[team][bot_name] = {}
        SLACK_BOT_TOKENS[team][bot_name]['verification_token'] = _v_token
        SLACK_BOT_TOKENS[team][bot_name]['oauth_token'] = _o_token
        SLACK_BOT_TOKENS[team][bot_name]['oauth_bot_token'] = _o_bot_token
        SLACK_BOT_TOKENS[team][bot_name]['app_id'] = bot_id

HANDLERS = _config.get('handlers')
HELP_CALLBACK = _config.get('help_callback')
DEFAULT_TO_HELP = _config.get('default_to_help', True)
LIST_PROVIDER_UPDATE_FREQUENCY = _config.get(
    'list_provider_update_frequency',
    120
)
WATCHER_SPAWN_WAIT_TIME_IN_SEC = _config.get(
    'watcher_spawn_wait_time_in_sec',
    5
)

# The SQS URL
# Example: http://localhost
SQS_URL = str_env('SQS_URL')
# SQS queue name for enqueuing webhooks
SQS_QUEUE_NAME = str_env('SQS_QUEUE_NAME')
# gevent pool concurrency for handling enqueued webhooks
WEBHOOK_WORKER_CONCURRENCY = int_env('WEBHOOK_WORKER_CONCURRENCY', 10)
# Match the sqs batch size to the webhook concurrency size, up to the sqs
# maximum of 10.
if WEBHOOK_WORKER_CONCURRENCY <= 10:
    _SQS_BATCH_SIZE_DEFAULT = WEBHOOK_WORKER_CONCURRENCY
else:
    _SQS_BATCH_SIZE_DEFAULT = 10
SQS_BATCH_SIZE = int_env(
    'SQS_BATCH_SIZE',
    _SQS_BATCH_SIZE_DEFAULT
)
SQS_MAX_POOL_CONNECTIONS = int_env(
    'SQS_MAX_POOL_CONNECTIONS',
    # Default to the webhook worker size, or 10, if that's lower.
    max(10, WEBHOOK_WORKER_CONCURRENCY)
)
SQS_VISIBILITY_TIMEOUT = int_env('SQS_VISIBILITY_TIMEOUT', 60)
SQS_WAIT_TIME_SECONDS = int_env('SQS_WAIT_TIME_SECONDS', 1)

# Redis settings

REDIS_PORT = int_env('REDIS_PORT', 6379)
REDIS_HOST = str_env('REDIS_HOST', 'localhost')


def get(name, default=None):
    """
    Get the value of a variable in the settings module scope.
    """
    return globals().get(name, default)
