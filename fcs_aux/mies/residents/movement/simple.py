import random
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses
from mies.buildings.utils import extract_bldg_coordinates
from mies.mongoconfig import get_db


class MovementBehavior:

    def choose_bldg(self, bldgs, addresses):
        candidates = []
        for bldg in bldgs:
            if not (bldg["occupied"] or bldg["processed"]):
                candidates.append(bldg)
        if candidates:
            bldg = random.choice(candidates)
            return bldg["address"], bldg
        else:
            return random.choice(addresses), None

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
                    "bldg": bldg["_id"],
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
        addresses = get_nearby_addresses(self.location)
        bldgs = load_nearby_bldgs(self.location)
        return addresses, bldgs
