from mies.redis_config import get_cache

DEFAULT_SMELL_EXPIRY = 24 * 60 * 60     # 1 day in seconds

SMELL_SOURCES_CACHE_PATTERN = "SMELL_SOURCE_"


def build_key(address):
    return SMELL_SOURCES_CACHE_PATTERN + address


def get_smell_sources():
    pattern = SMELL_SOURCES_CACHE_PATTERN + "*"
    cache = get_cache()
    for smell_source in cache.scan_iter(match=pattern):
        yield smell_source


def get_smell_source(address):
    key = build_key(address)
    cache = get_cache()
    cache.get(key)


def set_smell_source(address, strength, expiry=DEFAULT_SMELL_EXPIRY):
    key = build_key(address)
    cache = get_cache()
    cache.set(key, strength, expiry)


def update_smell_source(address, strength_delta):
    key = build_key(address)
    cache = get_cache()
    cache.hincrby(key, strength_delta)
