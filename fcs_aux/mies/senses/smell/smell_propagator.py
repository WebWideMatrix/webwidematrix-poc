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


def add_smell_to_bldg_and_containers(address, strength, cache, new_smells_key):
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
        count += add_smell_to_bldg_and_containers(address, strength, cache, new_smells_key)

        # draws rectangle around each smell source
        try:
            x, y = extract_bldg_coordinates(address)
        except:
            logging.error("This address is weird, can't propagate its smell: {}".format(address))
            continue

        count = propagate_smell_around_source(address, cache, count, new_smells_key, strength, x, y)

        t22 = datetime.utcnow()
        delta = t22 - t11
        times.append(delta.seconds * 1000 + delta.microseconds / 1000)


        # TODO propagate also vertically

    t2 = datetime.utcnow()
    if times:
        delta = t2 - t1
        logging.info("Smell propagation of {} sources took: {}ms".format(len(times), delta.seconds * 1000 + delta.microseconds / 1000))
        logging.info("Slowest source took: {}ms, fastest took: {}ms".format(max(times), min(times)))
        logging.info("Average time it took to propagate a smell source: {}ms".format(sum(times) / len(times)))
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
    count += add_smell_to_bldg_and_containers(address, strength, cache, new_smells_key)

    # draw rays of length (strength-1) the smell source, as approximation of real
    # propagation (for efficiency reasons)
    decreasing = range(-1, -strength, -1)
    increasing = range(1, strength)
    zeroes = [0] * (strength - 1)
    vectors = [
        zip(zeroes, decreasing),       # N
        zip(increasing, decreasing),   # NE
        zip(increasing, zeroes),       # E
        zip(increasing, increasing),   # SE
        zip(zeroes, increasing),       # S
        zip(decreasing, increasing),   # SW
        zip(decreasing, zeroes),       # W
        zip(decreasing, decreasing),   # NW
    ]
    for v in vectors:
        count += propagate_in_ray(x, y, v, address, count, strength, cache, new_smells_key)

    return count


def propagate_in_ray(x0, y0, vector, address, count, strength, *args):
    """
    Set a ray of decreasing smells in some vector from the given location
    :param x0: the center x location
    :param y0: the center y location
    :param vector: an array of points (Xdelta, Ydelta), representing a
           vector from the origin in some direction
    :param address: the full address of the location
    :param count: the current count of modifications, that should be updated
    :param strength: the initial smell strength
    :param args: the args to the function that updates smell
    :return: updated count
    """
    for s, delta in enumerate(vector):
        decreased_strength = strength - s - 1
        x, y = x0 + delta[0], y0 + delta[1]
        addr = replace_bldg_coordinates(address, x, y)
        count += add_smell_to_bldg_and_containers(addr, decreased_strength, *args)
    return count
