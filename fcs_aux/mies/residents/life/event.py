import random
from celery.utils.log import get_task_logger
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses, remove_occupant, add_occupant
from mies.celery import app
from mies.residents.movement.simple import occupy_bldg, occupy_empty_address
from mies.residents.object import Resident

logging = get_task_logger(__name__)


def choose_bldg(bldgs, addresses):
    candidates = []
    for bldg in bldgs:
        if not (bldg["occupied"] or bldg["processed"]):
            candidates.append(bldg)
    if candidates:
        bldg = random.choice(candidates)
        return bldg["address"], bldg
    else:
        return random.choice(addresses), None




@app.task(ignore_result=True)
def handle_life_event(resident_data):
    """

    :param resident:
    :return:
    """

    # TODO use Redis to improve data integrity
    logging.info("Resident {id} life event invoked..."
                 .format(id=resident_data["_id"]))
    resident = Resident(resident_data)

    location = resident_data["location"]

    # Check status of previous action.
    curr_bldg = load_bldg(resident_data["bldg"])
    if curr_bldg is not None:
        action_status = get_latest_action(curr_bldg)
        if is_action_pending(action_status):
            if should_discard_action(action_status):
                discard_action(curr_bldg, action_status)
            else:
                logging.info("Action in {addr} is still pending. "
                             "Doing nothing for now."
                             .format(addr=resident_data["bldg"]))
                return

        resident.update_energy_status_based_on_action_result(action_status)


    # read all near-by bldgs
    addresses = get_nearby_addresses(location)
    bldgs = load_nearby_bldgs(location)

    # choose a bldg to move into
    destination_addr, bldg = choose_bldg(bldgs, addresses)

    # update the bldg at the previous location (if existing),
    # that the resident has left the bldg
    remove_occupant(curr_bldg)

    # if moved into a bldg, update it to indicate that
    # the residents is inside
    if bldg:
        add_occupant(resident_data["_id"], bldg["_id"])

        occupy_bldg(resident_data, bldg)

        # if the bldg has payload that requires processing,
        # choose an action to apply to the payload


        # apply the action

    else:
        occupy_empty_address(resident_data, destination_addr)
