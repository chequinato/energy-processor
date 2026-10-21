import json
import logging

import redis

from .config import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


def cache_get(key):
    try:
        cached = redis_client.get(key)
    except redis.RedisError as e:
        logger.warning("Cache indisponível (get %s): %s", key, e)
        return None
    return json.loads(cached) if cached else None


def cache_set(key, value, ttl=None):
    try:
        redis_client.setex(key, ttl or settings.CACHE_TTL_SECONDS, json.dumps(value))
    except redis.RedisError as e:
        logger.warning("Cache indisponível (set %s): %s", key, e)


def cache_delete(*keys):
    try:
        redis_client.delete(*keys)
    except redis.RedisError as e:
        logger.warning("Cache indisponível (delete %s): %s", keys, e)


def cache_ping():
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False
