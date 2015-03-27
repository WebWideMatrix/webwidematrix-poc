import random
from celery.utils.log import get_task_logger
from mies.buildings.model import load_nearby_bldgs, get_nearby_addresses
from mies.celery import app

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
def handle_life_event(resident):
    logging.info("Resident {id} life event invoked..."
                 .format(id=resident["_id"]))

    location = resident["location"]
    # read all near-by bldgs
    addresses = get_nearby_addresses(location)
    bldgs = load_nearby_bldgs(location)

    # choose a bldg to move into
    destination_addr, bldg = choose_bldg(bldgs, addresses)

    # update the bldg at the previous location (if existing),
    # that the resident has left the bldg
    remove_occupant(resident.bldg);

    # if moved into a bldg, update it to indicate that
    # the residents is inside


    # if the bldg has payload that requires processing,
    # choose an action to apply to the payload


    # apply the action


    # update the resident energy level, according to the action success


