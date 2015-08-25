from mies.buildings.utils import get_bldg, get_flr_level
from mies.mongo_config import get_db
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


def update_bldg_stats(flr_address, stats):
    # ensure not being called more than once per second
    # TODO implement as decorator
    cache = get_cache()
    invocation_cache_key = "FUNC_CACHE_{}_{}".format("update_bldg_stats", flr_address)
    if cache.get(invocation_cache_key):
        return
    else:
        cache.set(invocation_cache_key, True)
        cache.expire(invocation_cache_key, 1)

    container_bldg_address = get_bldg(flr_address)
    assert container_bldg_address != flr_address
    flr_level = get_flr_level(flr_address)
    db = get_db()
    db.buildings.update({
            "_id": container_bldg_address
        },
        {
            "$set": {
                "flr_{level}_stats".format(level=flr_level): stats
            }
        }
    )


# TODO implement in decoupled signal handlers

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
