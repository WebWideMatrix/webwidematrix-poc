import logging
from pymongo import MongoClient
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT


STATUS_ACTIVE = "active"


def load_data_pipes(limit=100):
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    spec = {
        "status": STATUS_ACTIVE,
        "connectedBldg": {'$exists': True}
    }
    skip = 0
    done = False
    while not done:
        results = db.data_pipes.find(spec, limit=limit, skip=skip)
        yield results
        results = list(results)
        skip += len(results)
        done = len(results) < limit


def update_data_pipe(id, change):
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    db.data_pipes.update({"_id": id}, {"$set": change})
    logging.info("Updated data-pipe {}: {}".format(id, change))
