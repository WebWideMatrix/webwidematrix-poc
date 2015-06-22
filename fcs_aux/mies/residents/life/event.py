from celery.utils.log import get_task_logger
from mies.buildings.model import remove_occupant, add_occupant, load_bldg, create_buildings
from mies.celery import app
from mies.residents.acting.flow import update_bldg_with_results
from mies.residents.model import Resident

logging = get_task_logger(__name__)


def create_result_bldgs(curr_bldg, action_results):
    for r in action_results:
        key = r.get("key")
        content_type = r.get("content-type")
        payload = r.get("payload")
        placement_hints = r.get("placement_hints")

        if placement_hints.get("new_bldg"):
            flr = curr_bldg["flr"]  # same_flr is the default
            if placement_hints.get("flr_above"):
                flr_number = int(curr_bldg["flr"][1:]) + 1
                flr = "l{}".format(flr_number)
            # same_location is the default
            position_hints = {
                "near_x": curr_bldg["x"],
                "near_y": curr_bldg["y"],
            }
            create_buildings.s(content_type, [key], [payload], flr, position_hints).apply_async()

        else:
            # just update the current bldg
            update_bldg_with_results(curr_bldg, content_type, payload)



@app.task(ignore_result=True)
def handle_life_event(resident):
    """
    Periodic behavior of residents:
    * Check for a pending action in current bldg
    * Fetch the result of the action
    * Apply the result (update a bldg payload or create new ones)
    * Update energy status
    * Look at near-by bldgs
    * Choose a one to process or move to
    * Move to the chosen bldg
    * Choose an action to apply to the bldg's payload (if any)
    * Fire up the action
    :param resident: the acting resident
    :return:
    """

    if not isinstance(resident, Resident):
        resident = Resident(resident)

    # TODO use Redis to improve data integrity
    logging.info("Resident {id} life event invoked..."
                 .format(id=resident._id))

    # Check status of previous action.
    curr_bldg = load_bldg(_id=resident.bldg)
    if curr_bldg is not None and resident.processing:
        action_status = resident.get_latest_action(curr_bldg)
        action_result = resident.get_action_result(action_status)

        # check if action is still pending
        if action_status is not None and \
                        action_result is None and \
                resident.is_action_pending(action_status):
            if resident.should_discard_action(action_status):
                resident.discard_action(curr_bldg, action_status)
            else:
                logging.info("Action in {addr} is still pending. "
                             "Doing nothing for now."
                             .format(addr=resident.bldg))
                return
        else:
            # yay, we have results
            create_result_bldgs(curr_bldg, action_result)

        # if we got here, it means that no action is still pending
        resident.finish_processing(action_status, curr_bldg)

    # read all near-by bldgs
    addresses, bldgs = resident.look_around()

    # choose a bldg to move into
    destination_addr, bldg = resident.choose_bldg(bldgs, addresses)

    # update the bldg at the previous location (if existing),
    # that the resident has left the bldg
    if curr_bldg:
        remove_occupant(curr_bldg)

    # if moved into a bldg, update it to indicate that
    # the residents is inside
    if bldg:
        add_occupant(resident._id, bldg["_id"])

        resident.occupy_bldg(bldg)

        # if the bldg has payload that requires processing,
        if "payload" in bldg and not bldg["processed"]:
            # choose an action to apply to the payload
            action = resident.choose_action(bldg)

            # mark the resident & bldg as processing
            resident.mark_as_executing()

            # apply the action
            resident.start_action(action, bldg)

    else:
        resident.occupy_empty_address(destination_addr)
