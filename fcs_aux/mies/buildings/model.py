from collections import defaultdict
from datetime import datetime

import sys
from bson.json_util import dumps, loads
import random

from celery.utils.log import get_task_logger
from mies.buildings.stats import increment_bldgs, UNPROCESSED
from mies.buildings.utils import extract_bldg_coordinates, get_flr, time_print, get_bldg
from mies.celery import app
from mies.mongo_config import get_db
from mies.constants import FLOOR_W, FLOOR_H, PROXIMITY, DEFAULT_BLDG_ENERGY
from mies.redis_config import get_cache
from mies.senses.smell.smell_propagator import propagate_smell

MAX_PAYLOAD_SIZE = 10000

MAX_SUMMARY_SIZE = 1000

logging = get_task_logger(__name__)

ONE_DAY_IN_SECONDS = 60 * 60 * 24

FLR_KEYS = "KEYS_IN_{}"


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


def construct_bldg(flr, content_type, head, body, position_hints=None, is_composite=False,
                   db=None):
    """
    Constructs a bldg
    :param flr: the flr
    :param content_type: the content-type
    :param head: a dict of head attributes, such as: key, title, picture
    :param body: a dict of body payloads, such as:
        * summary_payload: basic summary details of the building content.
          This get persisted in the database.
        * raw_payload: the full content of the building. This doesn't get
          persisted in the databased, but only transiently stored in cache.
        * result_payload: content that should be persisted in the database.
          Note that this should be kept small.
    :param position_hints: hints to guide finding a location for the bldg
    :param is_composite: whether to mark the bldgs as composite ones
      (i.e., containing levels & inner bldgs)
    :param db: reference to the database
    :return:
    """
    x = 0
    y = 0
    address = None
    trials_state = _create_trials_state()
    while address is None:
        logging.info("Finding spot")
        address, x, y = find_spot(flr, trials_state, position_hints, db)
        if not is_vacant(address, db):
            address = None
            if position_hints is not None and "at_x" in position_hints:
                # if hints to use specific location, & it's caught, then move on
                position_hints.pop("at_x")
                position_hints.pop("at_y")

    # TODO revise to avoid infinite loop if no spot is available

    # logging.info(u"Creating building at: [{address}] '{text}'"
    #              .format(content_type=content_type,
    #                      address=address,
    #                      text=payload["text"]))
    if sys.getsizeof(body.get('summary_payload')) > MAX_SUMMARY_SIZE:
        logging.error("Summary is too big!")
        raise RuntimeError("Summary is too big! ({} bytes)"
                           .format(sys.getsizeof(body.get('summary_payload'))))
    if sys.getsizeof(body.get('result_payload')) > MAX_PAYLOAD_SIZE:
        logging.error("Payload is too big!")
        logging.info(body.get('result_payload'))
        raise RuntimeError("Payload is too big! ({} bytes)"
                           .format(sys.getsizeof(body.get('result_payload'))))
    return dict(
        address=address,
        flr=flr,
        x=x,
        y=y,
        createdAt=datetime.utcnow(),
        contentType=content_type,
        key=head.get('key'),
        picture=head.get('picture'),
        isComposite=is_composite,
        summary=body.get('summary_payload'),
        payload=body.get('result_payload'),
        processed=False,
        occupied=False,
        occupiedBy=None,
        energy=DEFAULT_BLDG_ENERGY
    )


@app.task(ignore_results=True)
def create_buildings(flr, content_type, heads, bodies, position_hints=None, is_composite=False,
                     write_to_cache=True, cache_period=ONE_DAY_IN_SECONDS):
    """
    Creates a batch of buildings.
    :param flr: the target floor in which to create the buildings
    :param content_type: the content-type of the buildings
    :param heads: the list of dicts containing the head attributes of the bldgs
    :param bodies: the list of dicts containing the payload attributes of the bldgs
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
        output_bldgs = []
        unique_buildings = []
        cache = get_cache()
        for b in buildings:
            existing = cache.hget(FLR_KEYS.format(flr), b["key"])
            if existing:
                output_bldgs.append(existing)
            else:
                unique_buildings.append(b)
        if not unique_buildings:
            return output_bldgs
        db.buildings.insert(unique_buildings)
        output_bldgs.extend([b["address"] for b in unique_buildings])
        if write_to_cache:
            # by default, we also want to cache newly created bldgs
            for j, bldg in enumerate(unique_buildings):
                # FIXME: create a Building class & instance & cache its serialization
                # the cache should also contain the raw-payload
                bldg["raw"] = bodies[j]["raw_payload"]
                cache.set(bldg["address"], dumps(bldg), ex=cache_period)
                cache.hset(FLR_KEYS.format(flr), bldg["key"], bldg["address"])
                cache.expire(FLR_KEYS.format(flr), cache_period)
        for bldg in unique_buildings:
            propagate_smell(bldg["address"], bldg["energy"])
        increment_bldgs(flr, UNPROCESSED, len(unique_buildings))
        return output_bldgs

    logging.info("C"*100)
    output_bldgs = []
    db = get_db()
    batch_size = 10
    buildings = []
    for i, head in enumerate(heads):
        bldg = construct_bldg(flr, content_type, head, bodies[i],
                              position_hints=position_hints, is_composite=is_composite,
                              db=db)
        buildings.append(bldg)
        if len(buildings) == batch_size:
            output_bldgs.extend(_create_batch_of_buildings())
            buildings = []
    if buildings:
        output_bldgs.extend(_create_batch_of_buildings())
    logging.info("Created {} buildings in {}".format(len(output_bldgs), flr))   # TODO subtract existing bldgs
    return output_bldgs


def get_nearby_addresses(address, proximity=10):
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


def load_raw_bldg(addr):
    logging.info("LRB-."*300)
    cache = get_cache()
    logging.info("Looking for bldg in cache at {}".format(addr))
    bldg = cache.get(addr)
    logging.info("Found:")
    logging.info(bldg.keys())
    if bldg is not None:
        logging.info("Not none & has raw? {}".format("raw" in bldg))
        return bldg.get("raw")
    return None


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
    cache = get_cache()
    key = FLR_KEYS.format(flr)
    count = cache.hlen(key)
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
        flr += 1
        result.append(flr)
    return result
