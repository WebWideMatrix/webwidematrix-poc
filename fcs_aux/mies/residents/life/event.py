from datetime import datetime

from bson import ObjectId
from kombu import uuid
from structlog import get_logger
from mies.buildings.model import remove_occupant, add_occupant, load_bldg, create_buildings
from mies.buildings.utils import get_flr_level, replace_flr_level, time_print
from mies.celery import app
from mies.redis_config import get_cache
from mies.residents.acting.flow import update_bldg_with_results
from mies.residents.model import Resident

logging = get_logger()

LIFE_EVENT_TASK_LOCK = "lock.resident.life_event.{}"
LOCK_EXPIRE = 60 * 10


def create_result_bldgs(curr_bldg, action_results):
    if action_results is None:
        logging.warn("No results for {}".format(curr_bldg["address"]))
        return
    for r in action_results:
        key = r.get("key")
        picture = r.get("picture")
        content_type = r.get("contentType")
        summary_payload = r.get("summary")
        raw_payload = r.get("raw")
        result_payload = r.get("payload")
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
            create_buildings(flr, content_type, [dict(key=key, picture=picture)],
                             [dict(summary_payload=summary_payload, raw_payload=raw_payload,
                                   result_payload=result_payload)],
                             position_hints)
        else:
            # just update the current bldg
            update_bldg_with_results(curr_bldg, content_type, summary_payload,
                                     raw_payload, result_payload)


def acquire_lock(resident_id):
    cache = get_cache()
    cache_key = LIFE_EVENT_TASK_LOCK.format(resident_id)
    if cache.get(cache_key) is None:
        cache.set(cache_key, True, ex=LOCK_EXPIRE)
        return True
    return False


def is_running(resident_id):
    cache = get_cache()
    cache_key = LIFE_EVENT_TASK_LOCK.format(resident_id)
    return cache.get(cache_key)


def release_lock(resident_id):
    cache = get_cache()
    cache_key = LIFE_EVENT_TASK_LOCK.format(resident_id)
    cache.delete(cache_key)


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
    if not acquire_lock(resident["_id"]):
        logging.warn("Resident {} previous life event is still ongoing, "
                     "aborting.".format(resident["_id"]))
        return

    life_event_id = uuid()
    global logging
    # if you need the worker id: worker=(current_process().index+1)
    logging = logging.bind(resident=resident["name"],
                           life_event_id=life_event_id)

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
                release_lock(resident["_id"])
                return
        else:
            logging.info("5"*100)
            # yay, we have results
            with time_print(logging, "create result bldg"):
                create_result_bldgs(curr_bldg, action_result)

        logging.info("6"*100)
        # if we got here, it means that no action is still pending
        with time_print(logging, "finish processing"):
            resident.finish_processing(action_status, curr_bldg)

    # choose a bldg to move into
    logging.info("~~BEFORE~~"*10)
    logging.info("BBBefore {}".format(resident.location))
    with time_print(logging, "choose bldg"):
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
        logging.info("Occupying bldg at: {}".format(destination_addr))
        add_occupant(resident._id, destination_bldg["_id"])

        resident.occupy_bldg(destination_bldg)

        # if the bldg has payload that requires processing,
        if "payload" in destination_bldg and not destination_bldg["processed"]:
            logging.info("Yay, found something to eat!!!!!!!!!!!!!!!")
            # choose an action to apply to the payload
            with time_print(logging, "choose action"):
                action = resident.choose_action(destination_bldg)

            # apply the action
            with time_print(logging, "sending action"):
                resident.start_processing(action, destination_bldg)
    else:
        logging.info("Moving to empty address: {}".format(destination_addr))
        resident.occupy_empty_address(destination_addr)

    resident.save()
    t2 = datetime.utcnow()
    delta = t2 - t1
    duration_in_ms = delta.seconds * 1000 + delta.microseconds / 1000
    logging.info("Resident life event took: {}ms".format(duration_in_ms))
    release_lock(resident["_id"])
