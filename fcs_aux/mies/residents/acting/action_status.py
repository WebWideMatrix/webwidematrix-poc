from datetime import datetime
from mies.mongoconfig import get_db


def update_action_status(bldg, action_status):
    # TODO have a Bldg class & move the method there
    db = get_db()
    db.buildings.update({
        "_id": bldg["_id"]
    }, {
        "$set": {
            "actionStatus": action_status
        }
    })


class ManageActionBehavior(object):

    def get_latest_action(self, bldg):
        """
        Get the most recent action logged in the given bldg.
        """
        if not bldg["actions"]:
            return None
        return bldg["actions"][-1]

    def is_action_pending(self, action_status):
        return "result" in action_status

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
