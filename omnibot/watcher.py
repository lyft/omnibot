import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent.pool # noqa:E402
import signal # noqa:E402
import json # noqa:E402
import logging # noqa:E402
import time # noqa:E402
import dateutil.parser # noqa:E402

import redis_lock # noqa:E402

from datetime import (
    datetime,
    timedelta
) # noqa:E402
from omnibot import settings # noqa:E402
from omnibot.services import omniredis # noqa:E402
from omnibot.services import stats # noqa:E402
from omnibot.services import slack # noqa:E402
from omnibot.services.slack.team import Team # noqa:E402
from omnibot.services.slack.bot import Bot # noqa:E402

STATE = {
    'shutdown': False
}
LOCK_EXPIRATION = 120


def bootstrap():
    global STATE

    watch_emoji()
    watch_ims()
    watch_mpims()
    watch_channels()
    watch_users()

    def finalizer(signal, frame):
        logger.info("SIGTERM caught, shutting down")
        STATE['shutdown'] = True
    signal.signal(signal.SIGTERM, finalizer)


def _is_allowed_to_run(redis_client, key):
    last_run_datetime_str = redis_client.get(key)
    if not last_run_datetime_str:
        return True
    last_run_datetime = dateutil.parser.parse(last_run_datetime_str)
    current_datetime = datetime.now()

    return current_datetime > last_run_datetime + timedelta(seconds=settings.LIST_PROVIDER_UPDATE_FREQUENCY)


def watch_users():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:users:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()
        with redis_lock.Lock(
                redis_client,
                'watch_users',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack user list.')
            with statsd.timer('watch.users'):
                for team_name, bot_name in settings.PRIMARY_SLACK_BOT.items():
                    team = Team.get_team_by_name(team_name)
                    bot = Bot.get_bot_by_name(team, bot_name)
                    slack.update_users(bot)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack user list.',
            exc_info=True
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_users
        )


def watch_channels():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:channels:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()
        with redis_lock.Lock(
                redis_client,
                'watch_channels',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack channel list.')
            with statsd.timer('watch.channels'):
                for team_name, bot_name in settings.PRIMARY_SLACK_BOT.items():
                    team = Team.get_team_by_name(team_name)
                    bot = Bot.get_bot_by_name(team, bot_name)
                    slack.update_channels(bot)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack channel list.',
            exc_info=True
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_channels
        )


def watch_groups():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:groups:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()
        with redis_lock.Lock(
                redis_client,
                'watch_groups',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack private channels list.')
            with statsd.timer('watch.groups'):
                bots = []
                for team_name, _bots in settings.SLACK_BOT_TOKENS.items():
                    for bot_name, bot_data in _bots.items():
                        team = Team.get_team_by_name(team_name)
                        bot = Bot.get_bot_by_name(team, bot_name)
                        bots.append(bot)
                slack.update_groups(bots)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack private channels list.',
            exc_info=True
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_groups
        )


def watch_ims():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:ims:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()
        with redis_lock.Lock(
                redis_client,
                'watch_ims',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack im channels list.')
            with statsd.timer('watch.ims'):
                bots = []
                for team_name, _bots in settings.SLACK_BOT_TOKENS.items():
                    for bot_name, bot_data in _bots.items():
                        team = Team.get_team_by_name(team_name)
                        bot = Bot.get_bot_by_name(team, bot_name)
                        bots.append(bot)
                slack.update_ims(bots)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack im channels list.',
            exc_info=True
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_ims
        )


def watch_mpims():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:mpims:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()

        with redis_lock.Lock(
                redis_client,
                'watch_mpims',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack mpim channels list.')
            with statsd.timer('watch.mpims'):
                bots = []
                for team_name, _bots in settings.SLACK_BOT_TOKENS.items():
                    for bot_name, bot_data in _bots.items():
                        team = Team.get_team_by_name(team_name)
                        bot = Bot.get_bot_by_name(team, bot_name)
                        bots.append(bot)
                slack.update_mpims(bots)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack mpim channels list.',
            exc_info=True
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_mpims
        )


def watch_emoji():
    try:
        redis_client = omniredis.get_redis_client(decode_responses=False)
        last_run_key = "watch:emoji:last_run_datetime"
        if not _is_allowed_to_run(redis_client, last_run_key):
            return

        statsd = stats.get_statsd_client()
        with redis_lock.Lock(
                redis_client,
                'watch_emoji',
                expire=LOCK_EXPIRATION,
                auto_renewal=True):
            logger.info('Updating slack emoji map.')
            with statsd.timer('watch.emoji'):
                for team_name, bot_name in settings.PRIMARY_SLACK_BOT.items():
                    team = Team.get_team_by_name(team_name)
                    bot = Bot.get_bot_by_name(team, bot_name)
                    slack.update_emoji(bot)
            redis_client.set(last_run_key, datetime.now().isoformat())
    except Exception:
        logger.exception(
            'Failed to update slack emoji list.',
            exc_info=True,
        )
    finally:
        return gevent.spawn_later(
            settings.WATCHER_SPAWN_WAIT_TIME_IN_SEC,
            watch_emoji,
        )


def main():
    bootstrap()
    while not STATE['shutdown']:
        gevent.sleep(1)


if __name__ == "__main__":
    from omnibot import setup_logging  # noqa:F401
    logger = logging.getLogger(__name__)
    main()
