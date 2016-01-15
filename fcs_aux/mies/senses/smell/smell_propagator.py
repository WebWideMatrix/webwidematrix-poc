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

    sources = get_smell_sources()
    times = []
    for source, strength in sources:
        # increments the containing bldgs smell
        if strength < 1:
            continue

        # now propagate the smell, taking out %10 & then 1 per distance unit
        strength = int(0.9 * strength)
        if strength < 1:
            continue

        t11 = datetime.utcnow()
        address = extract_address_from_key(source)
        count += add_smell_to_bldg_and_containers(address, cache, new_smells_key, strength)

        # draws rectangle around each smell source
        try:
            x, y = extract_bldg_coordinates(address)
        except:
            logging.error("This address is weird, can't propagate its smell: {}".format(address))
            continue

        count = propagate_smell_around_source(address, cache, count, new_smells_key, strength, x, y)

        t22 = datetime.utcnow()
        times.append((t22-t11).microseconds)


        # TODO propagate also vertically

    t2 = datetime.utcnow()
    if times:
        logging.info("Smell propagation of {} sources took: {}".format(len(times), (t2-t1).microseconds))
        logging.info("Slowest source took: {}, fastest took: {}".format(max(times), min(times)))
        logging.info("Average time it took to propagate a smell source: {}".format(sum(times) / len(times)))
    logging.info("Updated {} bldgs with smell".format(count))
    logging.info("Number of smell items: {}".format(cache.hlen(new_smells_key)))
    logging.info("S."*200)

    # update the pointer to the new smells
    def update_smells_pointer(pipe):
        current_smells_key = pipe.get(CURRENT_SMELLS_POINTER_KEY)
        pipe.set(CURRENT_SMELLS_POINTER_KEY, new_smells_key)
        pipe.delete(current_smells_key)
    cache.transaction(update_smells_pointer, CURRENT_SMELLS_POINTER_KEY)


def propagate_smell_around_source(address, cache, count, new_smells_key, strength, x, y):
    count += add_smell_to_bldg_and_containers(address, cache,
                                              new_smells_key, strength)

    # draw (strength-1) rings around the smell source, each having decreased strength
    for dist in xrange(1, strength):
        ring_strength = strength - dist

        for i in xrange(x - dist, x + dist + 1):
            # add top row
            addr = replace_bldg_coordinates(address, i, y - dist)
            count += add_smell_to_bldg_and_containers(addr, cache,
                                                      new_smells_key, ring_strength)
            # add bottom row
            addr = replace_bldg_coordinates(address, i, y + dist)
            count += add_smell_to_bldg_and_containers(addr, cache,
                                                      new_smells_key, ring_strength)

        for j in xrange(y - (dist - 1), y + (dist - 1) + 1):
            # add left col
            addr = replace_bldg_coordinates(address, x - dist, j)
            count += add_smell_to_bldg_and_containers(addr, cache,
                                                      new_smells_key, ring_strength)
            # add right col
            addr = replace_bldg_coordinates(address, x + dist, j)
            count += add_smell_to_bldg_and_containers(addr, cache,
                                                      new_smells_key, ring_strength)

    return count
