import statsd

from omnibot import settings

STATS_CLIENT = None


def get_statsd_client():
    global STATS_CLIENT
    if STATS_CLIENT is None:
        STATS_CLIENT = statsd.StatsClient(
            settings.STATSD_HOST,
            settings.STATSD_PORT,
            prefix=settings.STATSD_PREFIX
        )
    return STATS_CLIENT
