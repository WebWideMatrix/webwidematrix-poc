import os
from pymongo import MongoClient

DEFAULT_MONGO_HOST = 'localhost'
DEFAULT_MONGO_PORT = 27017
DEFAULT_MONGO_DB = 'w2m'


def get_config_var(name, default):
    return os.environ.get(name, default)


def get_db():
    mongo_host = get_config_var("MONGO_HOST", DEFAULT_MONGO_HOST)
    mongo_port = get_config_var("MONGO_PORT", DEFAULT_MONGO_PORT)
    mongo_db = get_config_var("MONGO_DB", DEFAULT_MONGO_DB)
    client = MongoClient(mongo_host, mongo_port)
    db = getattr(client, mongo_db)
    return db
