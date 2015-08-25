import operator
import random
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses, has_bldgs, get_bldg_flrs
from mies.buildings.stats import decrement_residents, increment_residents
from mies.buildings.utils import extract_bldg_coordinates, get_flr, get_flr_level, replace_flr_level
from mies.constants import GIVE_UP_ON_FLR, MAX_INTERACTION_RATE
from mies.mongo_config import get_db
from mies.senses.smell.smell_propagator import get_bldg_smell


VISION_POWER = 20


class NothingFoundException(Exception):
    pass


class MovementBehavior:

    def choose_bldg(self, curr_bldg):

        # if haven't smelled anything for a long time, give up
        # & get outside this flr
        if "moves_without_any_smell" in self and self.moves_without_any_smell > GIVE_UP_ON_FLR:
            self.get_outside(curr_bldg)
            self.reset_interactions_log()
        # if encountered many residents in the last hour, switch flr
        elif self.get_interactions_rate() > MAX_INTERACTION_RATE:
            self.randomly_switch_flr(curr_bldg)
            self.reset_interactions_log()


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
                self.log_interaction(bldg["occupiedBy"], bldg["address"])

        most_smelly = max(smells.iteritems(), key=operator.itemgetter(1))[0]
        if most_smelly < 1:
            most_smelly = random.choice(smells.keys())
        self.track_moves_without_smell(most_smelly < 1)
        bldg = candidates.get(most_smelly)
        return most_smelly, bldg

    def track_moves_without_smell(self, smelled_something):
        if not smelled_something:
            self.moves_without_any_smell += 1
        else:
            self.moves_without_any_smell = 0

    def occupy_bldg(self, bldg):
        curr_location = self.location
        x, y = extract_bldg_coordinates(curr_location)
        new_x, new_y = bldg["x"], bldg["y"]
        self.bldg = str(bldg["_id"])
        self.move_to(bldg["address"])
        self.velocity = [new_x - x, new_y - y]

    def occupy_empty_address(self, addr):
        curr_location = self.location
        x, y = extract_bldg_coordinates(curr_location)
        new_x, new_y = extract_bldg_coordinates(addr)
        self.bldg = None
        self.move_to(addr)
        self.velocity = [new_x - x, new_y - y]

    def look_around(self):
        assert self.location
        bldgs = load_nearby_bldgs(self.location)
        return bldgs

    def get_inside(self, curr_bldg):
        has_smell = False
        flr_level = 0
        while not has_smell:
            flr = curr_bldg["address"] + "-l" + str(flr_level)
            if not has_bldgs(flr):
                break
            has_smell = get_bldg_smell(flr) > 1
            if not has_smell:
                flr_level += 1

        if has_smell:
            self.location = flr + "-b(0,0)"
        else:
            raise NothingFoundException()

    def get_outside(self, curr_bldg):
        flr = get_flr(curr_bldg["address"])
        self.location = flr + "-b(0,0)"

    def randomly_switch_flr(self, curr_bldg):
        """
        Move up or down one flr randomly.
        :return:
        """
        flr = get_flr(curr_bldg["address"])
        flr_level = get_flr_level(flr)
        flrs = get_bldg_flrs(curr_bldg)
        # following code assumes bldg flrs start from 0, are consecutive & all populated
        if len(flrs) == 1:
            return
        elif flr_level == 0:
            # we're at the bottom flr, move up
            destination_flr = 1
        elif flr_level == flrs[-1]:
            # we're at the top flr, move down
            destination_flr = flrs[-2]
        else:
            # we're at the middle, so choose randomly whether to go up or down
            destination_flr = random.choice([flr_level - 1, flr_level + 1])

        self.switch_to_flr(curr_bldg, destination_flr)

    def switch_to_flr(self, curr_bldg, flr_level):
        new_addr = replace_flr_level(curr_bldg["address"], flr_level)
        self.move_to(new_addr)

    def move_to(self, address):
        decrement_residents(self.location)
        self.location = address
        increment_residents(self.location)
