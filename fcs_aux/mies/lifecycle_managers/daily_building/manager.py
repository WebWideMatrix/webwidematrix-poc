from datetime import datetime
import logging
from mies.celery import app
from mies.data_pipes.model import update_data_pipe, STATUS_ACTIVE
from mies.lifecycle_managers.daily_building import \
    DAILY_FEED_DISPATCHER_LIFEYCLE_MANAGER
from mies.mongoconfig import get_db
from mies.buildings.model import create_buildings

DAILY_FEED = "daily-feed"


def format_date(d):
    return d.strftime('%Y-%b-%d')


def _create_bldg(target_flr, today, data_pipe):
    payload = {
        "date": today,
        "data_pipes": [data_pipe["type"]]
    }
    address = create_buildings(content_type=DAILY_FEED, keys=[today],
                               payloads=[payload], flr=target_flr,
                               position_hints={"next_free": True})
    if type(address) == list:
        address = address[0]
    return address


def _update_data_pipe(address, data_pipe):
    update_data_pipe(data_pipe["_id"], {
        "connectedBldg": address
    })


def create_daily_bldg(db, today, manager):
    data_pipe = db.data_pipes.find_one({"_id": manager["dataPipe"]})
    if data_pipe is None or data_pipe.get("status") != STATUS_ACTIVE:
        # no need to create daily bldg if the data-pipe isn't active
        return
    user_bldg = db.buildings.find_one({"_id": manager["bldg"]})
    user_bldg_address = user_bldg["address"]
    target_flr = "{}-l0".format(user_bldg_address)
    existing_bldg = db.buildings.find_one({
        "flr": target_flr,
        "key": today
    })
    if existing_bldg is None:
        logging.info("Creating daily bldg '{today}' "
                     "inside {address}"
                     .format(today=today, address=user_bldg_address))
        address = _create_bldg(target_flr, today, data_pipe)
        _update_data_pipe(address, data_pipe)


@app.task(ignore_result=True)
def invoke():
    """
    Loops over all users and:
    * Looks up an existing bldg for the current date
    * If not found, creates one, next to the previous day
    * Connects any data-pipes for this user to the created bldg
    """
    logging.info("Invoking lifecycle manager...")
    today = format_date(datetime.utcnow())
    db = get_db()
    managers = db.lifecycle_managers.find(
        {"type": DAILY_FEED_DISPATCHER_LIFEYCLE_MANAGER}
    )
    # TODO read & process in batches
    for manager in managers:
        create_daily_bldg(db, today, manager)
