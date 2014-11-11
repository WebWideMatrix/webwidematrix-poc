from datetime import datetime
import logging
import random
from pymongo import MongoClient

from mies.celery import app
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT
from mies.buildings.constants import FLOOR_W, FLOOR_H


def build_bldg_address(flr, x, y):
    return flr + "-b(" + x + "," + y + ")"


def create_bldg(flr, near, content_type, payload):
    x = 0
    y = 0
    address = build_bldg_address(flr, x, y)
    found_spot = False

    def _find_spot():
        # generate a random address
        if near:
            # TODO
            pass
        else:
            x = random.randint(0, FLOOR_W)
            y = random.randint(0, FLOOR_H)
        address = build_bldg_address(flr, x, y)
        # TODO verify (using the cache) that it's free
        return address

    def _create_bldg():
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

    while not found_spot:
        found_spot = _find_spot()

    logging.info("Creating building for {content_type} at {address}: {text}"
                 .format(content_type=content_type,
                         address=address,
                         text=payload["text"]))
    return _create_bldg()


@app.task(ignore_results=True)
def create_buildings(content_type, payloads, flr, near=None):
    def _create_batch_of_buildings():
        # TODO handle errors
        db.buildings.insert(buildings)
        return len(buildings)

    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    batch_size = 10
    buildings = []
    count = 0
    for payload in payloads:
        buildings.append(create_bldg(flr, near, content_type, payload))
        if len(buildings) == batch_size:
            count += _create_batch_of_buildings()
            buildings = []
    if buildings:
        count += _create_batch_of_buildings()
    return count
