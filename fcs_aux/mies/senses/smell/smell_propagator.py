import logging
import time
from datetime import datetime

from mies.buildings.utils import extract_bldg_coordinates, replace_bldg_coordinates, calculate_distance, \
    get_bldg_containers
from mies.celery import app
from mies.constants import FLOOR_W, FLOOR_H
from mies.redis_config import get_cache
from mies.senses.smell.smell_source import get_smell_sources, extract_address_from_key

DEFAULT_SMELL_EXPIRY = 5 * 60     # 5 minutes in seconds

SMELL_CACHE_PATTERN = "SMELL_SOURCE_"

CURRENT_SMELLS_POINTER_KEY = "CURRENT_SMELLS"


def get_bldg_smell(addr):
    cache = get_cache()
    if cache.exists(CURRENT_SMELLS_POINTER_KEY):
        smells = cache.get(CURRENT_SMELLS_POINTER_KEY)
        smell = cache.hget(smells, addr)
        if smell is not None:
            return int(smell)
    else:
        logging.warning("No smells!!!")
        return 0


def build_key(address):
    return SMELL_CACHE_PATTERN + address


def add_smell_to_bldg_and_containers(address, cache, new_smells_key, strength):
    count = 0
    cache.hincrby(new_smells_key, address, strength)
    for addr in get_bldg_containers(address):
        cache.hincrby(new_smells_key, addr, strength)
        count += 1
    return count


@app.task(ignore_result=True)
def invoke():
    t1 = datetime.utcnow()
    logging.info("Smell"*200)
    logging.info("Propagating smells...")
    count = 0
    cache = get_cache()

    # create a new hset for the current smells
    new_smells_key = "current_smells_{}".format(time.time())

    for source, strength in get_smell_sources():
        # increments the containing bldgs smell
        if strength < 1:
            continue
        address = extract_address_from_key(source)
        count += add_smell_to_bldg_and_containers(address, cache, new_smells_key, strength)

        # now propagate the smell, taking out %10 & then 1 per distance unit
        strength = int(0.9 * strength)

        # draws rectangle around each smell source
        try:
            x, y = extract_bldg_coordinates(address)
        except:
            logging.error("This address is weird, can't propagate its smell: {}".format(address))
            continue
        for i in xrange(x - strength, x + strength):
            for j in xrange(y - strength, y + strength):
                if 0 < i < FLOOR_W and 0 < j < FLOOR_H:
                    curr_bldg_address = replace_bldg_coordinates(address, i, j)
                    distance = int(calculate_distance(curr_bldg_address, address))
                    delta = strength - distance
                    if delta > 0:
                        count += add_smell_to_bldg_and_containers(curr_bldg_address, cache,
                                                                  new_smells_key, delta)



        # TODO propagate also vertically

    t2 = datetime.utcnow()
    logging.info("Smell propagation task took: {}".format((t2-t1).seconds))
    logging.info("Updated {} bldgs with smell".format(count))
    logging.info("Number of smell items: {}".format(cache.hlen(new_smells_key)))
    logging.info("S."*200)

    # update the pointer to the new smells
    def update_smells_pointer(pipe):
        current_smells_key = pipe.get(CURRENT_SMELLS_POINTER_KEY)
        pipe.set(CURRENT_SMELLS_POINTER_KEY, new_smells_key)
        pipe.delete(current_smells_key)
    cache.transaction(update_smells_pointer, CURRENT_SMELLS_POINTER_KEY)
