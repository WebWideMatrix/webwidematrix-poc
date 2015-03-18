from mies.data_pipes.model import STATUS_ACTIVE
from mies.mongoconfig import get_db


def load_residents(criteria=None, limit=100):
    """
    Generator returning batches of data-pipe records
    :param limit: the size of each batch
    :return:
    """
    db = get_db()
    spec = {}
    if criteria is not None:
        spec.update(criteria)
    skip = 0
    done = False
    while not done:
        results = db.residents.find(spec, limit=limit, skip=skip)
        yield results
        results = list(results)
        skip += len(results)
        done = len(results) < limit
