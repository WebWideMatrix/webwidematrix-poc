from mies.redis_config import get_cache

DEFAULT_SMELL_SOURCE_EXPIRY = 24 * 60 * 60     # 1 day in seconds

SMELL_SOURCES_CACHE_PATTERN = "SMELL_SOURCE_"


def build_key(address):
    return SMELL_SOURCES_CACHE_PATTERN + address

def extract_address_from_key(key):
    return key[len(SMELL_SOURCES_CACHE_PATTERN):]

def get_smell_sources(page_size=100):
    pattern = SMELL_SOURCES_CACHE_PATTERN + "*"
    cache = get_cache()
    for key in cache.scan_iter(match=pattern):
        yield int(cache.get(key))


def get_smell_source(address):
    key = build_key(address)
    cache = get_cache()
    cache.get(key)


def create_smell_source(address, strength, expiry=DEFAULT_SMELL_SOURCE_EXPIRY):
    key = build_key(address)
    cache = get_cache()
    cache.set(key, strength, ex=expiry)


def update_smell_source(address, strength_delta):
    key = build_key(address)
    cache = get_cache()
    cache.hincrby(key, strength_delta)