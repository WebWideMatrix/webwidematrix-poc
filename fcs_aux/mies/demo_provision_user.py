import sys
import math
from datetime import datetime

from mongo_config import get_db
from constants import USER_CONTENT_TYPE, PERSONAL_TWITTER_FEED_DATA_PIPE, \
                      ACTIVE_STATUS, DAILY_FEED_DISPATCHER_LIFECYCLE_MANAGER, \
                      CONTENT_VISUALIZER_RESIDENT, DEFAULT_RESIDENT_ENERGY, \
                      DEFAULT_NUMBER_OF_RESIDENTS

###### USER

def create_user(username):
    user = {
        "username": username,
        "createdAt": datetime.utcnow(),
        "profile": {
            "language": "en",
            "picture": "https://pbs.twimg.com/profile_images/915446773627355136/ujyEpeuz_400x400.jpg",
            "screenName": username
        },
    }
    return user

def find_user(db, user):
    return db.users.find_one({"username": user["username"]})


def provision_user(db, user):
    existing = find_user(db, user)
    if existing:
        print "User already existed: %s" % existing["_id"]
        return existing["_id"]
    id = db.users.insert(user)
    print "User created: %s" % id
    return id

def update_user(db, user_id, changes):
    db.users.update({"_id": user_id}, {"$set": changes})
    print "Updated user %s: %s" % (user_id ,changes)


###### BLDG

def create_user_bldg(user):
    bldg = {
        "flr": "g",
        "key": user["username"],
        "address": "g-b(74, 26)",
        "x": 74,
        "y": 26,
        "contentType": USER_CONTENT_TYPE,
        "isComposite": True,
        "summary": user["profile"],
        "payload": user["profile"],
        "processed": False,
        "occupied": False,
        "occupiedBy": None
    }
    return bldg

def find_bldg(db, bldg):
    return db.buildings.find_one({"address": bldg["address"]})

def provision_bldg(db, bldg):
    existing = find_bldg(db, bldg)
    if existing:
        print "Bldg already existed: %s" % existing["_id"]
        return existing["_id"]
    id = db.buildings.insert(bldg)
    print "Bldg created: %s" % id
    return id


###### DATA PIPE

def create_user_data_pipe(user_id, access_token, access_token_secret):
    data_pipe = {
        "type": PERSONAL_TWITTER_FEED_DATA_PIPE,
        "userId": user_id,
        "status": ACTIVE_STATUS,
        "schedule": {
            "minutes_offset": datetime.utcnow().minute % 10
        },
        "tokens": {
            "accessToken": access_token,
            "accessTokenSecret": access_token_secret
        },
        "latestId": None,
        "connectedBldg": None,
        "frequency": None
    }
    return data_pipe

def find_data_pipe(db, data_pipe):
    return db.data_pipes.find_one({"userId": data_pipe["userId"]})

def provision_data_pipe(db, data_pipe):
    existing = find_data_pipe(db, data_pipe)
    if existing:
        print "Data-pipe already existed: %s" % existing["_id"]
        return existing["_id"]
    id = db.data_pipes.insert(data_pipe)
    print "Data-pipe created: %s" % id
    return id


###### LIFECYCLE MANAGER

def create_user_lifecycle_manager(user_id, bldg_id, data_pipe_id):
    lifecycle_manager = {
        "type": DAILY_FEED_DISPATCHER_LIFECYCLE_MANAGER,
        "userId": user_id,
        "status": ACTIVE_STATUS,
        "bldgId": bldg_id,
        "dataPipeId": data_pipe_id,
        "schedule": {
            "minutes": 0,
            "seconds": 0
        },
    }
    return lifecycle_manager

def find_lifecycle_manager(db, lifecycle_manager):
    return db.lifecycle_managers.find_one({"userId": lifecycle_manager["userId"]})

def provision_lifecycle_manager(db, lifecycle_manager):
    existing = find_lifecycle_manager(db, lifecycle_manager)
    if existing:
        print "Lifecycle-manager already existed: %s" % existing["_id"]
        return existing["_id"]
    id = db.lifecycle_managers.insert(lifecycle_manager)
    print "Lifecycle-manager created: %s" % id
    return id


###### RESIDENTS

def generate_resident_name(username, i):
    chars = ['a', 'b', 'c', 'd', 'e',
             'f', 'g', 'h', 'i', 'j',
             'k', 'l', 'm', 'n', 'o',
             'p', 'q', 'r', 's', 't',
             'u', 'v', 'w', 'x', 'y', 'z']
    return "{}{} {}".format(int(math.floor((i / len(chars)) + 1)),
                             chars[i % len(chars)], username)

def create_user_resident(user, bldg, i):
    resident = {
        "type": CONTENT_VISUALIZER_RESIDENT,
        "name": generate_resident_name(user["username"], i),
        "userId": user["_id"],
        "userProfileName": user["username"],
        "status": ACTIVE_STATUS,
        "bldgId": bldg["_id"],
        "processing": False,
        "acceleration": None,
        "velocity": None,
        "location": bldg["address"],
        "flr": bldg["flr"],
        "energy": DEFAULT_RESIDENT_ENERGY,
        "movesWithoutSmell": 0,
        "movesWithoutBldgs": 0
    }
    return resident

def find_resident(db, resident):
    return db.residents.find_one({"name": resident["name"]})

def provision_resident(db, resident):
    existing = find_resident(db, resident)
    if existing:
        print "Resident already existed: %s" % existing["_id"]
        return existing["_id"]
    id = db.residents.insert(resident)
    print "Resident created: %s" % id
    return id


###### MAIN

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: python demo_provision_user.py <username> <access token> <access token secret>"
        sys.exit(1)

    db = get_db()
    username = sys.argv[1]
    access_token = sys.argv[2]
    access_token_secret = sys.argv[3]
    user = create_user(username)
    user["_id"] = provision_user(db, user)
    bldg = create_user_bldg(user)
    bldg["_id"] = provision_bldg(db, bldg)
    update_user(db, user["_id"], {"bldg": {"_id": bldg["_id"], "address": bldg["address"]}})
    data_pipe = create_user_data_pipe(user["_id"], access_token, access_token_secret)
    data_pipe["_id"] = provision_data_pipe(db, data_pipe)
    update_user(db, user["_id"], {"dataPipes": [data_pipe["_id"]]})
    lifecycle_manager = create_user_lifecycle_manager(user["_id"], bldg["_id"], data_pipe["_id"])
    lifecycle_manager["_id"] = provision_lifecycle_manager(db, lifecycle_manager)
    update_user(db, user["_id"], {"lifecycleManagers": [lifecycle_manager["_id"]]})
    residents = [create_user_resident(user, bldg, i) for i in xrange(DEFAULT_NUMBER_OF_RESIDENTS)]
    resident_ids = [provision_resident(db, r) for r in residents]
    update_user(db, user["_id"], {"residents": resident_ids})
