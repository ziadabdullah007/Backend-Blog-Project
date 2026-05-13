import os
import redis


REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_TIMEOUT = float(os.getenv("REDIS_TIMEOUT", 1))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
    socket_connect_timeout=REDIS_TIMEOUT,
    socket_timeout=REDIS_TIMEOUT,
)


def cache_get(key: str):
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None


def cache_setex(key: str, ttl_seconds: int, value: str) -> bool:
    try:
        redis_client.setex(key, ttl_seconds, value)
        return True
    except redis.RedisError:
        return False


def cache_delete_pattern(pattern: str) -> None:
    try:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
    except redis.RedisError:
        pass