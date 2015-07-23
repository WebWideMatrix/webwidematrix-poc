import operator
import random
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses, has_bldgs
from mies.buildings.utils import extract_bldg_coordinates, get_flr
from mies.constants import GIVE_UP_ON_FLR
from mies.mongo_config import get_db
from mies.senses.smell.smell_propagator import get_bldg_smell


VISION_POWER = 20


class NothingFoundException(Exception):
    pass


class MovementBehavior:

    def choose_bldg(self, curr_bldg):

        # if haven't smelled anything for a long time, gice up & get outside this flr
        # TODO update movements_without_any_smell
        if self.movements_without_any_smell > GIVE_UP_ON_FLR:
            self.get_outside(curr_bldg)

        # if it's a composite bldg with smell, get inside
        if curr_bldg and curr_bldg["isComposite"] and get_bldg_smell(curr_bldg["address"]):
            self.get_inside(curr_bldg)

        # get all near-by bldgs & smells
        # Note: assuming same vision & smelling power
        bldgs = self.look_around()
        smells = self.smell_around()

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

    def get_inside(self, curr_bldg):
        has_smell = True
        flr_level = 0
        while not has_smell:
            flr = curr_bldg["address"] + "-l" + str(flr_level)
            if has_bldgs(flr):
                has_smell = get_bldg_smell(flr) > 1

        if has_smell:
            self.location = flr + "-b(0,0)"
        else:
            raise NothingFoundException()

    def get_outside(self, curr_bldg):
        flr = get_flr(curr_bldg["address"])
        self.location = flr + "-b(0,0)"
