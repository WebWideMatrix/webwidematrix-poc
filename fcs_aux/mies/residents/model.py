from mies.mongoconfig import get_db
from mies.residents.acting.flow import ActingBehavior


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
        results = [Resident(r) for r in results]
        yield results
        skip += len(results)
        done = len(results) < limit


class Resident(dict, ActingBehavior):
    def __init__(self, data, **kwargs):
        super(Resident, self).__init__(**kwargs)
        self.update(data)
