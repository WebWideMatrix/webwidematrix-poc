from collections import defaultdict
from datetime import datetime
import logging
import random
from pymongo import MongoClient

from mies.celery import app
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT
from mies.buildings.constants import FLOOR_W, FLOOR_H, PROXIMITY


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
    for x in xrange(FLOOR_H):
        for y in xrange(FLOOR_W):
            if is_vacant(build_bldg_address(flr, x, y), db):
                return x, y
    raise NoSpotLeft()


def find_spot(flr, state=None, position_hints=None, db=None):
    if state is None:
        state = _create_trials_state()
    # calculate the address according to the hints
    position_hints = position_hints or {}
    near_x = position_hints.get('near_x')
    near_y = position_hints.get('near_y')
    next_free = position_hints.get('next_free') or False
    if near_x is not None and near_y is not None:
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


def construct_bldg(flr, content_type, key, payload, position_hints=None, db=None):
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
        payload=payload,
        processed=False,
        occupied=False,
        occupiedBy=None
    )


@app.task(ignore_results=True)
def create_buildings(content_type, keys, payloads, flr, position_hints=None):
    """
    Creates a batch of buildings.
    :param content_type: the content-type of the buildings
    :param keys: the list of keys for the buildings
    :param payloads: the list of payloads for the buildings
    :param flr: the target floor in which to create the buildings
    :param position_hints: dict of hints where to position the new buildings, such as:
    * near_x: x coordinate, near which the buildings will be created
    * near_y: y coordinate, near which the buildings will be created
    * next_free: if True, create the buildings in the next free place (sequentially)
    :return: the addresses of the created buildings.
    """
    def _create_batch_of_buildings():
        # TODO handle errors
        db.buildings.insert(buildings)
        return len(buildings)

    created_addresses = []
    # TODO abstract the DB & inject it
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    batch_size = 10
    buildings = []
    count = 0
    for i, payload in enumerate(payloads):
        bldg = construct_bldg(flr, content_type, keys[i], payload, position_hints, db)
        buildings.append(bldg)
        created_addresses.append(bldg["address"])
        if len(buildings) == batch_size:
            count += _create_batch_of_buildings()
            buildings = []
    if buildings:
        count += _create_batch_of_buildings()
    logging.info("Created {} buildings in {}".format(count, flr))
    return created_addresses
