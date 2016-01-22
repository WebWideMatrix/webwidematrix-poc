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
        yield (key, int(cache.get(key)))


def get_smell_source(address):
    key = build_key(address)
    cache = get_cache()
    return cache.get(key)


def create_smell_source(address, strength, expiry=DEFAULT_SMELL_SOURCE_EXPIRY):
    key = build_key(address)
    cache = get_cache()
    cache.set(key, strength, ex=expiry)


def update_smell_source(address, strength_delta):
    key = build_key(address)
    cache = get_cache()
    if strength_delta > 0:
        cache.incr(key, strength_delta)
    else:
        cache.decr(key, strength_delta)


def create_or_update_smell_source(address, strength,
                                  expiry=DEFAULT_SMELL_SOURCE_EXPIRY):
    """
    Creates a smell source cache entry, or updates it if it already exists.
    :param address: smell source location
    :param strength: the smell strength, which equals the bldg energy
    :param expiry: expiry time of the smell source in the cache
    :return: the smell strength change
    """
    existing = get_smell_source(address)
    if existing is None:
        create_smell_source(address, strength, expiry)
        delta = strength
    else:
        update_smell_source(address, strength)
        delta = strength - existing
    return delta
