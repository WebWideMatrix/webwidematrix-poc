from collections import defaultdict
from datetime import datetime
import logging
import random
from pymongo import MongoClient

from mies.celery import app
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT
from mies.buildings.constants import FLOOR_W, FLOOR_H, PROXIMITY


def build_bldg_address(flr, x, y):
    return "{flr}-b({x},{y})".format(flr=flr, x=x, y=y)


def is_vacant(address):
    # TODO implement using cache
    return True


def _create_trials_state():
    trials_state = defaultdict(int)
    trials_state["near_lookups_count"] = 0
    trials_state["proximity"] = PROXIMITY
    return trials_state


def find_spot(flr, state=None, near_x=None, near_y=None):
    if state is None:
        state = _create_trials_state()
    # generate a random address
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
    else:
        x = random.randint(0, FLOOR_W)
        y = random.randint(0, FLOOR_H)
    return build_bldg_address(flr, x, y), x, y


def construct_bldg(flr, near_x, near_y, content_type, key, payload):
    # TODO revise to add more hints than just near
    x = 0
    y = 0
    address = None
    trials_state = _create_trials_state()
    while address is None:
        address, x, y = find_spot(flr, trials_state, near_x, near_y)
        if not is_vacant(address):
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
def create_buildings(content_type, keys, payloads, flr, near_x=None, near_y=None,
                     next_free=False):
    """
    Creates a batch of buildings.
    :param content_type: the content-type of the buildings
    :param keys: the list of keys for the buildings
    :param payloads: the list of payloads for the buildings
    :param flr: the target floor in which to create the buildings
    :param near_x: optional x coordinate, near which the buildings will be created
    :param near_y: optional y coordinate, near which the buildings will be created
    :param next_free: optional hint to create the buildings in the next free place
    (sequentially)
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
        bldg = construct_bldg(flr, near_x, near_y, content_type, keys[i], payload)
        buildings.append(bldg)
        create_buildings.append(bldg["address"])
        if len(buildings) == batch_size:
            count += _create_batch_of_buildings()
            buildings = []
    if buildings:
        count += _create_batch_of_buildings()
    logging.info("Created {} buildings in {}".format(count, flr))
    return create_buildings
