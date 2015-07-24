from mies.mongo_config import get_db
from mies.residents.acting.flow import ActingBehavior
from mies.residents.movement.simple import MovementBehavior
from mies.residents.sensing.smell_sense_behavior import SmellingBehavior


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


class Resident(dict, ActingBehavior, MovementBehavior, SmellingBehavior):
    def __init__(self, data, **kwargs):
        super(Resident, self).__init__(**kwargs)
        self.update(data)
        self["_initial"] = data
        self["_changes"] = {}

    def __getattribute__(self, item):
        try:
            return super(Resident, self).__getattribute__(item)
        except:
            return self[item]

    def __setattr__(self, key, value):
        self["_changes"][key] = value
        super(Resident, self).__setattr__(key, value)

    def save(self):
        db = get_db()
        db.residents.update(
            {"_id": self._id},
            {
                "$set": self["_changes"]
            })
        self["_changes"] = {}
