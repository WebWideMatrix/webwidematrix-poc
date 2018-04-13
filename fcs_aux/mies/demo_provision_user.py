import sys
from datetime import datetime

from mongo_config import get_db
from twitter_config import CONSUMER_KEY, CONSUMER_SECRET
from constants import USER_CONTENT_TYPE, PERSONAL_TWITTER_FEED_DATA_PIPE, ACTIVE_STATUS

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
    print "User created: " + id
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

def create_user_data_pipe(user_id):
    data_pipe = {
        "type": PERSONAL_TWITTER_FEED_DATA_PIPE,
        "userId": user_id,
        "status": ACTIVE_STATUS,
        "schedule": {
            "minutes_offset": datetime.utcnow().minute % 10
        },
        "tokens": {
            "accessToken": CONSUMER_KEY,
            "accessTokenSecret": CONSUMER_SECRET
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


###### MAIN

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python demo_provision_user.py <username>"
        sys.exit(1)

    db = get_db()
    username = sys.argv[1]
    user = create_user(username)
    user["_id"] = provision_user(db, user)
    bldg = create_user_bldg(user)
    bldg["_id"] = provision_bldg(db, bldg)
    update_user(db, user["_id"], {"bldg": {"_id": bldg["_id"], "address": bldg["address"]}})
    data_pipe = create_user_data_pipe(user["_id"])
    data_pipe["_id"] = provision_data_pipe(db, data_pipe)
    update_user(db, user["_id"], {"dataPipes": [data_pipe["_id"]]})
    # TODO lifecycle manager

    # TODO residents

    
