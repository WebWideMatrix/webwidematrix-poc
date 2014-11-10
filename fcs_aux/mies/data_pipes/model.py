from pymongo import MongoClient
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT


def load_data_pipes(limit=100):
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    spec = {
        "active": True,
        "connectedBldg": {'$exists': True}
    }
    skip = 0
    done = False
    while not done:
        results = db.data_pipes.find(spec, limit=limit, skip=skip)
        skip += len(results)
        yield results
        done = len(results) < limit
