import operator
import random
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses
from mies.buildings.utils import extract_bldg_coordinates
from mies.mongo_config import get_db


VISION_POWER = 20


class MovementBehavior:

    def choose_bldg(self, bldgs, smells):
        candidates = {}
        for bldg in bldgs:
            if not bldg["occupied"]:
                candidates[bldg["address"]] = bldg
            else:
                smells.pop(bldg["address"])

        most_smelly = max(smells.iteritems(), key=operator.itemgetter(1))[0]
        if most_smelly < 1:
            most_smelly = random.choice(smells.keys())
        bldg = candidates.get(most_smelly)
        return most_smelly, bldg

    def occupy_bldg(self, bldg):
        curr_location = self.location
        x, y = extract_bldg_coordinates(curr_location)
        new_x, new_y = bldg["x"], bldg["y"]
        velocity = [new_x - x, new_y - y]
        db = get_db()
        db.residents.update(
            {"_id": self._id},
            {
                "$set":
                {
                    "bldg": str(bldg["_id"]),
                    "location": bldg["address"],
                    "velocity": velocity
                }
            })

    def occupy_empty_address(self, addr):
        curr_location = self.location
        x, y = extract_bldg_coordinates(curr_location)
        new_x, new_y = extract_bldg_coordinates(addr)
        velocity = [new_x - x, new_y - y]
        db = get_db()
        db.residents.update(
            {"_id": self._id},
            {
                "$set":
                {
                    "bldg": None,
                    "location": addr,
                    "velocity": velocity
                }
            })

    def look_around(self):
        assert self.location
        bldgs = load_nearby_bldgs(self.location)
        return bldgs
