import logging
from mies.mongoconfig import get_db


STATUS_ACTIVE = "active"


def load_data_pipes(criteria=None, limit=100):
    """
    Generator returning batches of data-pipe records
    :param limit: the size of each batch
    :return:
    """
    db = get_db()
    spec = {
        "status": STATUS_ACTIVE,
        "connectedBldg": {'$exists': True}
    }
    if criteria is not None:
        spec.update(criteria)
    skip = 0
    done = False
    while not done:
        results = db.data_pipes.find(spec, limit=limit, skip=skip)
        yield results
        results = list(results)
        skip += len(results)
        done = len(results) < limit


def update_data_pipe(data_pipe_id, change):
    db = get_db()
    db.data_pipes.update({"_id": data_pipe_id}, {"$set": change})
    logging.info("Updated data-pipe {}: {}".format(data_pipe_id, change))
