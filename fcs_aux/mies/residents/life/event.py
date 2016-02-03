from datetime import datetime

from bson import ObjectId
from celery.utils.log import get_task_logger
from mies.buildings.model import remove_occupant, add_occupant, load_bldg, create_buildings
from mies.buildings.utils import get_flr_level, replace_flr_level
from mies.celery import app
from mies.residents.acting.flow import update_bldg_with_results
from mies.residents.model import Resident

logging = get_task_logger(__name__)


def create_result_bldgs(curr_bldg, action_results):
    if action_results is None:
        logging.warn("No results for {}".format(curr_bldg["address"]))
        return
    for r in action_results:
        key = r.get("key")
        content_type = r.get("contentType")
        summary_payload = r.get("summary_payload")
        raw_payload = r.get("raw_payload")
        result_payload = r.get("result_payload")
        placement_hints = r.get("placement_hints")

        if placement_hints.get("new_bldg"):
            flr = curr_bldg["flr"]  # same_flr is the default
            if placement_hints.get("flr_above"):
                flr_level = get_flr_level(curr_bldg["flr"])
                flr = replace_flr_level(curr_bldg["flr"], flr_level + 1)
            # same_location is the default
            position_hints = {
                "at_x": curr_bldg["x"],
                "at_y": curr_bldg["y"],
            }
            # FIXME: this was getting stuck in the queue. Must be done async.
            # create_buildings.s(content_type, [key], [payload], flr, position_hints).apply_async(
            #     queue='bldg_creation', routing_key='bldg.create'
            # )
            t1 = datetime.utcnow()
            create_buildings(content_type, [key], [summary_payload], [raw_payload],
                             [result_payload], flr, position_hints)
            t2 = datetime.utcnow()
            delta = t2 - t1
            logging.info("Creating result buildings took: {}".format(delta.seconds))
        else:
            # just update the current bldg
            update_bldg_with_results(curr_bldg, content_type, summary_payload,
                                     raw_payload, result_payload)


@app.task(ignore_result=True)
def handle_life_event(resident):
    """
    Periodic behavior of residents:
    * Check for a pending action in current destination_bldg
    * Fetch the result of the action
    * Apply the result (update a destination_bldg payload or create new ones)
    * Update energy status
    * Check whether it's a composite destination_bldg with smell, & if so get inside
    * Check whether no smell for too long, & if so get outside
    * Look at near-by bldgs
    * Choose a one to process or move to
    * Move to the chosen destination_bldg
    * Choose an action to apply to the destination_bldg's payload (if any)
    * Fire up the action
    :param resident: the acting resident
    :return:
    """
    t1 = datetime.utcnow()
    logging.info(" a "*100)
    logging.info(type(resident))
    logging.info(resident)
    if not isinstance(resident, Resident):
        logging.info(" a1 "*100)
        resident = Resident(resident)
        logging.info(type(resident))
        logging.info(resident)

    # TODO use Redis to improve data integrity
    logging.info("Resident {name} life event invoked..."
                 .format(name=resident.name))

    # Check status of previous action.
    curr_bldg = load_bldg(_id=ObjectId(resident.bldg)) if resident.bldg else None
    logging.info("0"*100)
    logging.info(resident.bldg)
    logging.info(resident.processing)
    if curr_bldg is not None and resident.processing:
        logging.info("1"*100)
        action_status = resident.get_latest_action(curr_bldg)
        logging.info(action_status)
        action_result = resident.get_action_result(action_status)
        # logging.info(action_result)
        # check if action is still pending
        if action_status is not None and \
                        action_result is None and \
                resident.is_action_pending(action_status):
            logging.info("2"*100)
            if resident.should_discard_action(action_status):
                resident.discard_action(curr_bldg, action_status)
                logging.info("3"*100)
            else:
                logging.info("4"*100)
                logging.info("Action in {addr} is still pending. "
                             "Doing nothing for now."
                             .format(addr=resident.bldg))
                return
        else:
            logging.info("5"*100)
            # yay, we have results
            create_result_bldgs(curr_bldg, action_result)

        logging.info("6"*100)
        # if we got here, it means that no action is still pending
        resident.finish_processing(action_status, curr_bldg)

    # choose a bldg to move into
    logging.info("~~BEFORE~~"*10)
    logging.info("BBBefore {}".format(resident.location))
    destination_addr, destination_bldg = resident.choose_bldg(curr_bldg)
    logging.info("~~AFTER~~"*10)
    logging.info("AAAfter {}".format(resident.location))

    # update the bldg at the previous location (if existing),
    # that the resident has left the bldg
    if curr_bldg:
        remove_occupant(curr_bldg)

    # if moved into a bldg, update it to indicate that
    # the residents is inside
    if destination_bldg:
        add_occupant(resident._id, destination_bldg["_id"])

        resident.occupy_bldg(destination_bldg)

        # if the bldg has payload that requires processing,
        if "payload" in destination_bldg and not destination_bldg["processed"]:
            # choose an action to apply to the payload
            action = resident.choose_action(destination_bldg)

            # apply the action
            resident.start_processing(action, destination_bldg)

    else:
        resident.occupy_empty_address(destination_addr)

    resident.save()
    t2 = datetime.utcnow()
    delta = t2 - t1
    duration_in_ms = delta.seconds * 1000 + delta.microseconds / 1000
    logging.info("Resident life event took: {}ms".format(duration_in_ms))
