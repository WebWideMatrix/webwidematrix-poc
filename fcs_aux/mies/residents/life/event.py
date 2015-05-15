from celery.utils.log import get_task_logger
from mies.buildings.model import remove_occupant, add_occupant, load_bldg
from mies.celery import app
from mies.residents.model import Resident

logging = get_task_logger(__name__)


@app.task(ignore_result=True)
def handle_life_event(resident):
    """
    Periodic behavior of residents:
    * Check for a pending action in current bldg
    * Fetch the result of the action
    * Apply the result (update a bldg payload or create new ones)
    * UPdate energy status
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
        resident.occupy_empty_address(resident, destination_addr)
