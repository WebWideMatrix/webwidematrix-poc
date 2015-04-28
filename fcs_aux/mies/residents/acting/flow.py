from datetime import datetime
from mies.buildings.constants import DEFAULT_BLDG_ENERGY
from mies.mongoconfig import get_db


def update_action_status(bldg, action_status):
    # TODO have a Bldg class & move the method there
    actions = bldg["actions"]
    actions[-1] = action_status
    db = get_db()
    db.buildings.update({
        "_id": bldg["_id"]
    }, {
        "$set": {
            "actions": actions
        }
    })


class ActingBehavior:

    def finish_processing(self, action_status, bldg):
        bldg_energy = bldg["energy"] or DEFAULT_BLDG_ENERGY
        success = action_status["successLevel"]
        energy_gained = bldg_energy * success

        db = get_db()

        db.residents.update({
            "_id": self["_id"]
        }, {
            "$set": {
                "processing": False,
                "energy": self["energy"] + energy_gained
            }
        })
        curr_bldg_energy = bldg["energy"] or DEFAULT_BLDG_ENERGY

        db.buildings.update({
            "_id": bldg["_id"]
        }, {
            "$set": {
                "processed": (energy_gained > 0),
                "energy": curr_bldg_energy - energy_gained
            }
        })

    def get_latest_action(self, bldg):
        """
        Get the most recent action logged in the given bldg.
        TODO move to Bldg class
        """
        if not bldg["actions"]:
            return None
        return bldg["actions"][-1]

    def is_action_pending(self, action_status):
        return "result" not in action_status

    def should_discard_action(self, action_status):
        """
        Action should be discarded in case:
        * it didn't complete in 24h
        * its result is ERROR
        :param action_status:
        :return:
        """
        if (datetime.now() - action_status["startedAt"]).seconds > 60 * 60 * 24:
            return True
        if action_status["result"] == "ERROR":
            return True
        return False

    def discard_action(self, bldg, action_status):
        action_status["endedAt"] = datetime.now()
        action_status["status"] = "DISCARDED"
        update_action_status(bldg, action_status)

    def choose_action(self, bldg):
        pass

    def execute_action(self, action, bldg):
        pass