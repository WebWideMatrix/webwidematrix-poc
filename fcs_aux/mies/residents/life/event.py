from celery.utils.log import get_task_logger
from mies.buildings.model import load_nearby_bldgs
from mies.celery import app

logging = get_task_logger(__name__)


@app.task(ignore_result=True)
def handle_life_event(resident):
    logging.info("Resident {id} life event invoked..."
                 .format(id=resident["_id"]))

    # read all near-by bldgs
    bldgs = load_nearby_bldgs()

    # choose a bldg to move into


    # update the bldg at the previous location (if existing),
    # that the resident has left the bldg


    # if moved into a bldg, update it to indicate that
    # the residents is inside


    # if the bldg has payload that requires processing,
    # choose an action to apply to the payload


    # apply the action


    # update the resident energy level, according to the action success


