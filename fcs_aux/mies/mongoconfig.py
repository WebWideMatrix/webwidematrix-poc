from pymongo import MongoClient

# TODO use env vars
MONOGO_HOST = 'localhost'
MONOGO_PORT = 3001
MONGO_DB = 'meteor'


def get_db():
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    db = getattr(client, MONGO_DB)
    return db
