import os
from redis import StrictRedis

DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0


def get_config_var(name, default):
    return os.environ.get(name, default)


def get_cache():
    redis_host = get_config_var("REDIS_HOST", DEFAULT_REDIS_HOST)
    redis_port = get_config_var("REDIS_PORT", DEFAULT_REDIS_PORT)
    redis_db = get_config_var("REDIS_DB", DEFAULT_REDIS_DB)
    cache = StrictRedis(redis_host, redis_port, redis_db)
    return cache
