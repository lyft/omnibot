import redis
import functools

from omnibot import settings


@functools.lru_cache(maxsize=4)
def get_redis_client(decode_responses=True):
    return redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        charset="utf-8",
        decode_responses=decode_responses
    )
