from datetime import datetime
import random

from mies.constants import DEFAULT_BLDG_ENERGY
from mies.buildings.model import logging
from mies.celery import app
from mies.mongo_config import get_db
from mies.senses.smell.smell_source import update_smell_source


def update_action_status(bldg, action_status):
    # TODO have a Bldg class & move the method there
    actions = bldg.get("actions", [])
    actions[-1] = action_status
    db = get_db()
    db.buildings.update({
        "_id": bldg["_id"]
    }, {
        "$set": {
            "actions": actions
        }
    })
    logging.info("Updated bldg {} action status: {}".format(
        bldg["address"], action_status))


def add_new_action_status(bldg, action_status):
    # TODO have a Bldg class & move the method there
    actions = bldg.get("actions", [])
    actions.append(action_status)
    db = get_db()
    db.buildings.update({
        "_id": bldg["_id"]
    }, {
        "$set": {
            "actions": actions
        }
    })
    logging.info("Added new action status to bldg {}: {}".format(
        bldg["address"], action_status))


def update_bldg_processed_status(bldg, energy_change):
    # TODO have a Bldg class & move the method there
    curr_bldg_energy = bldg["energy"] or DEFAULT_BLDG_ENERGY
    change = {
        "processed": (energy_change < 0),
        "energy": curr_bldg_energy + energy_change
    }
    db = get_db()
    db.buildings.update({
                            "_id": bldg["_id"]
                        }, {
                            "$set": change
                        })
    update_smell_source(bldg["address"], energy_change)
    logging.info("Updated bldg {} processed status: {}".format(
        bldg["address"], change))


def update_bldg_with_results(bldg, content_type, payload):
    # TODO have a Bldg class & move the method there
    change = {}
    if content_type and content_type != bldg["contentType"]:
        change["contentType"] = content_type
    if payload:
        bldg["payload"].update(payload)
        change["payload"] = bldg["payload"]

    db = get_db()
    db.buildings.update({
                            "_id": bldg["_id"]
                        }, {
                            "$set": change
                        })
    logging.info("Updated bldg {} with results".format(bldg["address"]))


class ActingBehavior:

    def update_processing_status(self, is_processing, energy_gained=0):
        db = get_db()
        db.residents.update({
                                "_id": self._id
                            }, {
                                "$set": {
                                    "processing": is_processing,
                                    "energy": self.energy + energy_gained
                                }
                            })

    def finish_processing(self, action_status, bldg):
        bldg_energy = bldg["energy"] or DEFAULT_BLDG_ENERGY
        success = action_status["successLevel"]
        energy_gained = bldg_energy * success
        self.update_processing_status(False, energy_gained)
        update_bldg_processed_status(bldg, -energy_gained)

    def get_latest_action(self, bldg):
        """
        Get the most recent action logged in the given bldg.
        TODO move to Bldg class
        """
        if not bldg["actions"]:
            return None
        return bldg["actions"][-1]

    def is_action_pending(self, action_status):
        """
        TODO move to Bldg class
        """
        return "endedAt" not in action_status

    def should_discard_action(self, action_status):
        """
        Action should be discarded in case:
        * it didn't complete in 24h
        * its result is ERROR
        :param action_status:
        :return:
        """
        if (datetime.utcnow() - action_status["startedAt"]).seconds > 60 * 60 * 24:
            return True
        if action_status["result"] == "ERROR":
            return True
        return False

    def discard_action(self, bldg, action_status):
        action_status["endedAt"] = datetime.utcnow()
        action_status["status"] = "DISCARDED"
        update_action_status(bldg, action_status)

    def get_registered_actions(self, content_type):
        """
        Stub implementation
        TODO lookup actions registered for given content-type
        """
        registered_actions = {
            "twitter-social-post": ["fetch-article"]
        }
        return registered_actions.get(content_type)

    def choose_action(self, bldg):
        """
        Stub implementation.
        TODO lookup registered actions by content-type
        TODO extract features from bldg payload
        TODO predict the success of each action
        TODO return the action with highest predicted success
        """
        registered_actions = self.get_registered_actions(bldg["contentType"])
        return random.choice(registered_actions)

    def mark_as_executing(self):
        # mark resident as processing
        self.update_processing_status(True)

    def start_action(self, action, bldg):
        task = app.send_task(action, [bldg["payload"]])
        action_status = {
            "startedAt": datetime.utcnow(),
            "startedBy": self._id,
            "action": action,
            "result_id": task.task_id
        }
        add_new_action_status(bldg, action_status)

    def get_action_result(self, action_status):
        result_id = action_status["result_id"]
        result = app.AsyncResult(result_id)
        if result.ready():
            try:
                return result.get(timeout=1)
            except:
                pass
        return None
