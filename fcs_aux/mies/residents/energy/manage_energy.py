from mies.buildings.constants import DEFAULT_BLDG_ENERGY
from mies.mongoconfig import get_db


def update_bldg_energy(bldg, energy):
    db = get_db()
    db.buildings.update({
        "_id": bldg["_id"]
    }, {
        "$set": {
            "energy": energy
        }
    })


class ManageEnergyBehavior(object):

    def update_energy_status_based_on_action_result(self, action_status, bldg):
        bldg_energy = bldg["energy"] or DEFAULT_BLDG_ENERGY
        success = action_status["successLevel"]
        energy_gained = bldg_energy * success
        self.update_energy(self["energy"] + energy_gained)
        update_bldg_energy(bldg, bldg_energy - energy_gained)

    def update_energy(self, energy):
        db = get_db()
        db.residents.update({
            "_id": self["_id"]
        }, {
            "$set": {
                "energy": energy
            }
        })
