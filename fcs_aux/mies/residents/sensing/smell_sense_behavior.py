from mies.buildings.model import get_nearby_addresses
from mies.senses.smell.smell_propagator import get_bldg_smell


SMELLING_POWER = 20


class SmellingBehavior:

    def smell_around(self):
        assert self.location
        addresses = get_nearby_addresses(self.location)
        return {addr: get_bldg_smell(addr) for addr in addresses}
