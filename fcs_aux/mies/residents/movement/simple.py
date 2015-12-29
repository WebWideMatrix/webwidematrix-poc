import logging
import random
from mies.buildings.model import load_nearby_bldgs, has_bldgs, get_bldg_flrs, get_nearby_addresses
from mies.buildings.stats import decrement_residents, increment_residents
from mies.buildings.utils import extract_bldg_coordinates, get_flr, get_flr_level, replace_flr_level
from mies.constants import GIVE_UP_ON_FLR, MAX_INTERACTION_RATE, FLOOR_H, FLOOR_W
from mies.senses.smell.smell_propagator import get_bldg_smell
from mies.lifecycle_managers.daily_building.manager import _build_user_current_bldg_cache_key
from mies.redis_config import get_cache

VISION_POWER = 20


class NothingFoundException(Exception):
    pass


def _build_resident_location_cache_key(addr):
    return "OCCUPIED_{}".format(addr)



class MovementBehavior:

    def choose_bldg(self, curr_bldg):

        # get the current bldg for the user
        logging.info("Choosing bldg for {}".format(self.name))
        user_id = self.userId
        logging.info(self)
        curr_user_bldg_key = _build_user_current_bldg_cache_key(user_id)
        cache = get_cache()
        curr_user_bldg_address = cache.get(curr_user_bldg_key)
        logging.info("   &&&CUR_BLDG {}".format(curr_bldg))
        if curr_bldg:
            logging.info("   &&&CUR_BLDG_ADDR {}".format(curr_bldg["address"]))
            logging.info("   &&&CUR_BLDG_ADDR_STARTSW {}".format(curr_bldg["address"].startswith(curr_user_bldg_address)))

        # if curr_bldg is None or not curr_bldg["address"].startswith(curr_user_bldg_address):
        if not self.location.startswith(curr_user_bldg_address):
            # this means we're in some old bldg, move to the current one
            logging.info("---------^^^^^^^*********"*100)
            self.move_to(curr_user_bldg_address + "-l0-b(0,0)")

        # if haven't smelled anything for a long time, give up
        # & get outside this flr
        if self.movesWithoutSmell > GIVE_UP_ON_FLR:
            self.get_outside()
            self.reset_interactions_log()
        # if encountered many residents in the last hour, switch flr
        elif self.get_interactions_rate() > MAX_INTERACTION_RATE:
            self.randomly_switch_flr()
            self.reset_interactions_log()


        # if it's a composite bldg with smell, get inside
        if curr_bldg and curr_bldg["isComposite"] and get_bldg_smell(curr_bldg["address"]):
            self.get_inside(curr_bldg)

        # get all near-by bldgs & smells
        # Note: assuming same vision & smelling power

        bldgs = self.look_around()      # dict: addr->bldg
        smells = self.smell_around()    # dict: addr->smell
        neighbours = self.look_for_neighbours_around()  # dict: addr->neighbour

        logging.info("XX smells:")
        logging.info(self.log_perception(smells, bldgs, neighbours))

        most_smelly_addr = None
        max_smell = -1
        occupied = []
        for addr, smell in smells.iteritems():
            # don't move to a place caught by another resident
            if neighbours.get(addr):
                occupied.append(addr)
                self.log_interaction(neighbours[addr], addr)
            # double check whether this is a bldg & it's occupied
            elif bldgs.get(addr) and bldgs[addr]["occupied"]:
                occupied.append(addr)
                self.log_interaction(bldgs[addr]["occupiedBy"], addr)
            elif smell is not None:
                if smell > max_smell:
                    most_smelly_addr = addr
                    max_smell = smell

        # don't consider occupied addresses
        for addr in occupied:
            del smells[addr]

        if max_smell <= 0:
            most_smelly_addr = random.choice(smells.keys())

        self.track_moves_without_smell(max_smell <= 0)
        bldg = bldgs.get(most_smelly_addr)
        return most_smelly_addr, bldg

    def log_perception(self, smells, bldgs, rsdts):
        logging.info("LP "*100)
        logging.info("ATTTTTT: {}".format(self.location))
        min_x, min_y = 1000, 1000
        max_x, max_y = 0, 0

        def render_cell(addr, smell, self_location):
            cell = ""
            if addr == self_location:
                cell = "*"
            else:
                if bldgs.get(addr):
                    cell = "{}B".format(cell)
                if rsdts.get(addr):
                    cell = "{}R".format(cell)
                if cell == "":
                    cell = smell or ""
            return cell

        def update_actual_range(x, y, min_x, min_y, max_x, max_y):
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
            return min_x, min_y, max_x, max_y

        flr = []
        for row in xrange(FLOOR_H):
            flr.append(["."]*FLOOR_W)

        for addr, smell in smells.iteritems():
            x, y = extract_bldg_coordinates(addr)
            min_x, min_y, max_x, max_y = \
                update_actual_range(x, y, min_x, min_y, max_x, max_y)
            flr[y][x] = render_cell(addr, smell, self.location)

        logging.info('---')
        logging.info("Rendering {} in range: {},{} - {},{}"
                     .format(self.name, min_x, min_y, max_x, max_y))
        area = []
        for j in range(min_y, max_y):
            area.append(flr[j][min_x:max_x])
        logging.info('\n\n' + '\n'.join([''.join(['{:2}'.format(item) for item in row])
                                         for row in area]))
        logging.info('---')

    def track_moves_without_smell(self, smelled_something):
        if not smelled_something:
            self.movesWithoutSmell += 1
        else:
            self.movesWithoutSmell = 0

    def occupy_bldg(self, bldg):
        logging.info("OCCUPY "*10)
        logging.info(bldg)
        curr_location = self.location
        x, y = extract_bldg_coordinates(curr_location)
        new_x, new_y = bldg["x"], bldg["y"]
        self.bldg = str(bldg["_id"])
        logging.info(self.bldg)
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
        logging.info("LA "*30)
        logging.info("AAAAT {}".format(self.location))
        return load_nearby_bldgs(self.location)

    def look_for_neighbours_around(self):
        assert self.location
        cache = get_cache()
        addresses = get_nearby_addresses(self.location)
        result = {}
        logging.info("r"*100)
        logging.info("r"*100)
        for addr in addresses:
            rsdt = cache.get(_build_resident_location_cache_key(addr))
            if rsdt:
                logging.info(rsdt)
                result[addr] = rsdt
        logging.info("r"*100)
        logging.info("r"*100)
        return result

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

    def get_outside(self):
        flr = get_flr(self.location)
        self.location = flr + "-b(0,0)"

    def randomly_switch_flr(self):
        """
        Move up or down one flr randomly.
        :return:
        """
        flr = get_flr(self.location)
        flr_level = get_flr_level(flr)
        flrs = get_bldg_flrs(self.location)
        # following code assumes bldg flrs start from 0, are consecutive & all populated
        if len(flrs) <= 1:
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

        self.switch_to_flr(destination_flr)

    def switch_to_flr(self, flr_level):
        new_addr = replace_flr_level(self.location, flr_level)
        self.move_to(new_addr)

    def move_to(self, address):
        prev_loc = self.location
        cache = get_cache()
        ret = cache.delete(_build_resident_location_cache_key(prev_loc))
        logging.info("Delete returned: {}".format(ret))
        self.location = address
        # record in cache that a resident is in that location
        cache.set(_build_resident_location_cache_key(address), self.name, ex=60)
        if get_flr(prev_loc) != get_flr(address):
            self.flr = get_flr(address)
            # switched flr - update stats
            decrement_residents(prev_loc)
            increment_residents(self.location)
