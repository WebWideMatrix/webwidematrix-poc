from mies.buildings.model import update_bldg_stats
from mies.redis_config import get_cache

NUM_RESIDENTS_CACHE_KEY = "residents_in_{address}"
NUM_BLDGS_CACHE_KEY = "{status}_bldgs_in_{address}"

UNPROCESSED = "unprocessed"
BEING_PROCESSED = "being_processed"
PROCESSED = "processed"

PROCESSING_STATUSES = (
    UNPROCESSED,
    BEING_PROCESSED,
    PROCESSED
)

_build_residents_cache_key = lambda address: NUM_RESIDENTS_CACHE_KEY.format(address=address)
_build_bldgs_cache_key = lambda address, status: NUM_BLDGS_CACHE_KEY.format(address=address,
                                                                            status=status)


def get_stats(address):
    # TODO add all stats: unprocessed/being_processed/processed
    cache = get_cache()
    return {
        "residents": cache.get(_build_residents_cache_key(address)),
        "unprocessed_bldgs": cache.get(_build_bldgs_cache_key(address, UNPROCESSED)),
        "being_processed_bldgs": cache.get(_build_bldgs_cache_key(address, BEING_PROCESSED)),
        "processed_bldgs": cache.get(_build_bldgs_cache_key(address, PROCESSED)),
    }


def increment_residents(flr_address, amount=1):
    cache = get_cache()
    cache.incr(_build_residents_cache_key(flr_address), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))


def decrement_residents(flr_address, amount=1):
    cache = get_cache()
    cache.decr(_build_residents_cache_key(flr_address), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))


def increment_bldgs(flr_address, processing_status, amount=1):
    assert processing_status in PROCESSING_STATUSES
    cache = get_cache()
    cache.incr(_build_bldgs_cache_key(flr_address, processing_status), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))


def decrement_bldgs(flr_address, processing_status, amount=1):
    assert processing_status in PROCESSING_STATUSES
    cache = get_cache()
    cache.decr(_build_bldgs_cache_key(flr_address, processing_status), amount)
    update_bldg_stats(flr_address, get_stats(flr_address))
