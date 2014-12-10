import logging
from pymongo import MongoClient
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT


STATUS_ACTIVE = "active"


def load_data_pipes(limit=100):
    """
    Generator returning batches of data-pipe records
    :param limit: the size of each batch
    :return:
    """
    # TODO abstract the DB & inject it
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


def update_data_pipe(data_pipe_id, change):
    # TODO abstract the DB & inject it
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    db.data_pipes.update({"_id": data_pipe_id}, {"$set": change})
    logging.info("Updated data-pipe {}: {}".format(data_pipe_id, change))
