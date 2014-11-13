from datetime import datetime
import logging
import random
from pymongo import MongoClient

from mies.celery import app
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT
from mies.buildings.constants import FLOOR_W, FLOOR_H, PROXIMITY


def build_bldg_address(flr, x, y):
    return "{flr}-b({x},{y})".format(flr=flr, x=x, y=y)


def construct_bldg(flr, near_x, near_y, content_type, payload):

    def _is_vacant(_address):
        # TODO implement using cache
        return True

    def _find_spot(state):
        # generate a random address
        if near_x is not None and near_y is not None:
            state['near_lookups_count'] += 1
            # have we almost exhausted the near by spots?
            if state['near_lookups_count'] > (2 * state['proximity'])**2:
                # if so, extend the lookup area
                state['proximity'] *= 2
            _x = random.randint(near_x - state['proximity'], near_x + state['proximity'])
            _y = random.randint(near_y - state['proximity'], near_y + state['proximity'])
        else:
            _x = random.randint(0, FLOOR_W)
            _y = random.randint(0, FLOOR_H)
        return build_bldg_address(flr, _x, _y), x, y

    x = 0
    y = 0
    address = None
    trials_state = dict(near_lookups_count=0,
                        proximity=PROXIMITY)
    while address is None:
        address, x, y = _find_spot(trials_state)
        if not _is_vacant(address):
            address = None

    logging.info(u"Creating building at: [{address}] '{text}'"
                 .format(content_type=content_type,
                         address=address,
                         text=payload["text"]))
    return dict(
        address=address,
        flr=flr,
        x=x,
        y=y,
        createdAt=datetime.utcnow(),
        contentType=content_type,
        payload=payload,
        processed=False,
        occupied=False,
        occupiedBy=None
    )


@app.task(ignore_results=True)
def create_buildings(content_type, payloads, flr, near_x=None, near_y=None):
    def _create_batch_of_buildings():
        # TODO handle errors
        db.buildings.insert(buildings)
        return len(buildings)

    logging.info("About to create buildings in flr {}".format(flr))
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    batch_size = 10
    buildings = []
    count = 0
    for payload in payloads:
        buildings.append(construct_bldg(flr, near_x, near_y, content_type, payload))
        if len(buildings) == batch_size:
            count += _create_batch_of_buildings()
            buildings = []
    if buildings:
        count += _create_batch_of_buildings()
    logging.info("Created {} buildings in {}".format(count, flr))
    return count
