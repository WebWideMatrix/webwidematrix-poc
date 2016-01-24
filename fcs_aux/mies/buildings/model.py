from collections import defaultdict
from datetime import datetime
from bson.json_util import dumps, loads
import random

from celery.utils.log import get_task_logger
from mies.buildings.stats import increment_bldgs, UNPROCESSED
from mies.buildings.utils import extract_bldg_coordinates, get_flr
from mies.celery import app
from mies.mongo_config import get_db
from mies.constants import FLOOR_W, FLOOR_H, PROXIMITY, DEFAULT_BLDG_ENERGY
from mies.redis_config import get_cache
from mies.senses.smell.smell_propagator import propagate_smell

logging = get_task_logger(__name__)

ONE_DAY_IN_SECONDS = 60 * 60 * 24


class NoSpotLeft(Exception):
    pass


def build_bldg_address(flr, x, y):
    return "{flr}-b({x},{y})".format(flr=flr, x=x, y=y)


def is_vacant(address, db):
    # TODO implement using cache
    # TODO abstract the DB & inject it
    bldg = db.buildings.find_one({"address": address})
    return bldg is None


def _create_trials_state():
    trials_state = defaultdict(int)
    trials_state["near_lookups_count"] = 0
    trials_state["proximity"] = PROXIMITY
    return trials_state


def _get_next_free(flr, db):
    for y in xrange(FLOOR_H):
        for x in xrange(FLOOR_W):
            if is_vacant(build_bldg_address(flr, x, y), db):
                return x, y
    raise NoSpotLeft()


def find_spot(flr, state=None, position_hints=None, db=None):
    if state is None:
        state = _create_trials_state()
    # calculate the address according to the hints
    position_hints = position_hints or {}
    at_x = position_hints.get('at_x')
    at_y = position_hints.get('at_y')
    near_x = position_hints.get('near_x')
    near_y = position_hints.get('near_y')
    next_free = position_hints.get('next_free') or False
    if at_x is not None and at_y is not None:
        x = at_x
        y = at_y
    elif near_x is not None and near_y is not None:
        state['near_lookups_count'] += 1
        # have we almost exhausted the near by spots?
        if state['near_lookups_count'] > (2 * state['proximity'])**2:
            # if so, extend the lookup area
            state['proximity'] *= 2
        x = random.randint(near_x - state['proximity'],
                           near_x + state['proximity'])
        y = random.randint(near_y - state['proximity'],
                           near_y + state['proximity'])
    elif next_free:
        x, y = _get_next_free(flr, db)
    else:
        x = random.randint(0, FLOOR_W)
        y = random.randint(0, FLOOR_H)
    return build_bldg_address(flr, x, y), x, y


def construct_bldg(flr, content_type, key, payload, position_hints=None,
                   is_composite=False, db=None):
    x = 0
    y = 0
    address = None
    trials_state = _create_trials_state()
    while address is None:
        address, x, y = find_spot(flr, trials_state, position_hints, db)
        if not is_vacant(address, db):
            address = None

    # TODO revise to avoid infinite loop if no spot is available

    # logging.info(u"Creating building at: [{address}] '{text}'"
    #              .format(content_type=content_type,
    #                      address=address,
    #                      text=payload["text"]))
    return dict(
        address=address,
        flr=flr,
        x=x,
        y=y,
        createdAt=datetime.utcnow(),
        contentType=content_type,
        key=key,
        isComposite=is_composite,
        payload=payload,
        processed=False,
        occupied=False,
        occupiedBy=None,
        energy=DEFAULT_BLDG_ENERGY
    )


@app.task(ignore_results=True)
def create_buildings(content_type, keys, payloads, flr,
                     position_hints=None, is_composite=False,
                     write_to_cache=True, cache_period=ONE_DAY_IN_SECONDS):
    """
    Creates a batch of buildings.
    :param content_type: the content-type of the buildings
    :param keys: the list of keys for the buildings
    :param payloads: the list of payloads for the buildings
    :param flr: the target floor in which to create the buildings
    :param position_hints: dict of hints where to position
      the new buildings, such as:
      * near_x: x coordinate, near which the buildings will be created
      * near_y: y coordinate, near which the buildings will be created
      * next_free: if True, create the buildings in the next
      free place (sequentially)
    :param is_composite: whether to mark the bldgs as composite ones
      (i.e., containing levels & inner bldgs)
    :param write_to_cache: whether to store the bldgs also in cache,
      which by default is True.
    :param cache_ttl: how much time should the bldgs stay in cache, which
      by default is 1 day
    :return: the addresses of the created buildings.
    """
    def _create_batch_of_buildings():
        # TODO handle errors
        db.buildings.insert(buildings)
        if write_to_cache:
            # by default, we also want to cache newly created bldgs
            cache = get_cache()
            for bldg in buildings:
                # FIXME: create a Building class & instance & cache its serialization
                cache.set(bldg["address"], dumps(bldg), ex=cache_period)
        for bldg in buildings:
            propagate_smell(bldg["address"], bldg["energy"])
        increment_bldgs(flr, UNPROCESSED, len(buildings))
        return len(buildings)

    logging.info("C"*100)
    created_addresses = []
    db = get_db()
    batch_size = 10
    buildings = []
    count = 0
    for i, payload in enumerate(payloads):
        bldg = construct_bldg(flr, content_type, keys[i], payload,
                              position_hints, is_composite, db)
        buildings.append(bldg)
        created_addresses.append(bldg["address"])
        if len(buildings) == batch_size:
            count += _create_batch_of_buildings()
            buildings = []
    if buildings:
        count += _create_batch_of_buildings()
    logging.info("Created {} buildings in {}".format(count, flr))
    return created_addresses


def get_nearby_addresses(address, proximity=50):
    # generate a list of neighbour addresses
    addresses = []
    flr = get_flr(address)
    center_x, center_y = extract_bldg_coordinates(address)
    for x in range(center_x - proximity / 2, center_x + proximity / 2):
        for y in range(center_y - proximity / 2, center_y + proximity / 2):
            if not (x == center_x and y == center_y) and \
               0 < x < FLOOR_W and 0 < y < FLOOR_H:
                addresses.append("{flr}-b({x},{y})".format(flr=flr, x=x, y=y))
    return addresses


def load_bldg(**kwargs):
    db = get_db()
    return db.buildings.find_one(kwargs)


def load_nearby_bldgs(address):
    addresses = get_nearby_addresses(address)
    # query the cache for any bldg whose address is one of these addresses
    result = {}
    cache = get_cache()
    for addr in addresses:
        bldg = cache.get(addr)
        if bldg is not None:
            result[addr] = loads(bldg)

    if not result:
        db = get_db()
        bldgs = db.buildings.find({
            "address": {
                "$in": addresses
            }
        })
        for b in bldgs:
            result[b["address"]] = b
    return result


def add_occupant(bldg_id, resident_id):
    db = get_db()
    db.buildings.update(
        {"_id": bldg_id},
        {
            "$set":
            {
                "occupiedBy": resident_id,
                "occupied": True
            }
        })


def remove_occupant(bldg):
    db = get_db()
    db.buildings.update(
        {"_id": bldg["_id"]},
        {
            "$set":
            {
                "occupiedBy": None,
                "occupied": False
            }
        })


def has_bldgs(flr):
    db = get_db()
    count = db.buildings.find({
        "flr": flr
    }).count()
    return count > 0


def get_bldg_flrs(bldg_addr):
    """
    return the flr levels of a bldg that have bldgs inside them.
    assumes that the 1st level has bldgs inside it.
    :param bldg:
    :return:
    """
    result = []
    flr = 0
    while has_bldgs("{bldg}-l{flr}".format(bldg=bldg_addr, flr=flr)):
        result.append(flr)
    return result
