from mies.buildings.model import update_bldg_stats
from mies.redis_config import get_cache

NUMBER_OF_RESIDENTS_CACHE_KEY = "residents_in_{address}"


def _build_residents_cache_key(address):
    return NUMBER_OF_RESIDENTS_CACHE_KEY.format(address)


def get_stats(address):
    # TODO add all stats: unprocessed/being_processed/processed
    cache = get_cache()
    return {
        "residents": cache.get(_build_residents_cache_key(address))
    }


def increment_residents(flr_address, amount=1):
    cache = get_cache()
    cache.incr(_build_residents_cache_key(flr_address), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))


def decrement_residents(flr_address, amount=1):
    cache = get_cache()
    cache.decr(_build_residents_cache_key(flr_address), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))
