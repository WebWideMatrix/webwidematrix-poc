from datetime import datetime
import logging
from pymongo import MongoClient
from mies.celery import app
from mies.data_pipes.model import update_data_pipe, STATUS_ACTIVE
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT
from mies.buildings.model import create_buildings

DAILY_FEED = "daily-feed"


def format_date(d):
    # return d.strftime('%Y-%b-%d')
    return d.strftime('%Y-%b-%d-%H%:%M')


def _create_bldg(target_flr, today, user):
    payload = {
        "date": today,
        "data_pipes": [dp["type"] for dp in user["dataPipes"]]
    }
    address = create_buildings(content_type=DAILY_FEED, keys=[today],
                               payloads=[payload], flr=target_flr,
                               next_free=True),
    return address


def _update_data_pipes(address, user):
    for dp in user["dataPipes"]:
        if dp["status"] == STATUS_ACTIVE:
            update_data_pipe(dp["_id"], {
                "connectedBldg": address
            })


def create_daily_bldg_for_user(db, today, user):
    user_bldg_address = user["bldg"]["address"]
    target_flr = "{}-l0".format(user_bldg_address)
    existing_bldg = db.buildings.find({
        "flr": target_flr,
        "key": today
    })
    if existing_bldg is not None:
        logging.info("Daily bldg ({today}) already existed for user {user}"
                     .format(today=today, user=user["screenName"]))
    else:
        address = _create_bldg(target_flr, today, user)
        _update_data_pipes(address, user)


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
    # TODO abstract the DB & inject it
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = client.meteor
    users = db.users.find()
    for user in users:
        create_daily_bldg_for_user(db, today, user)
