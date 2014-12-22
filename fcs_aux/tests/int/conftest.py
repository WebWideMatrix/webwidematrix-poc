from datetime import datetime
from pymongo import MongoClient
import pytest
from mies.mongoconfig import MONOGO_HOST, MONOGO_PORT


@pytest.fixture(scope="module")
def db_name():
    return "meteor"


@pytest.fixture(scope="module")
def db(db_name):
    # TODO abstract the DB & inject it
    # TODO use a test db
    client = MongoClient(MONOGO_HOST, MONOGO_PORT)
    return getattr(client, db_name)


@pytest.fixture(scope="module")
def some_bldg_flr():
    return "g-b(67,37)-l4"


@pytest.fixture(scope="module")
def some_bldg_location():
    return 65, 12


@pytest.fixture(scope="module")
def some_bldg_address():
    return "g-b(67,37)-l4-b(65,12)"


@pytest.fixture(scope="module")
def some_bldg_content_type():
    return "some-type"


@pytest.fixture(scope="module")
def some_bldg_key():
    return "some-type"


@pytest.fixture(scope="module")
def some_bldg_payload():
    return {
        "field1": "value 1",
        "field2": "value 2",
        "field3": "value 3",
    }


@pytest.fixture(scope="module")
def create_some_bldg(request, db, some_bldg_flr, some_bldg_location,
                     some_bldg_address, some_bldg_content_type,
                     some_bldg_key, some_bldg_payload):
    x, y = some_bldg_location
    _id = db.buildings.insert({
        "address": some_bldg_address,
        "flr": some_bldg_flr,
        "x": x,
        "y": y,
        "createdAt": datetime.utcnow(),
        "contentType": some_bldg_content_type,
        "key": some_bldg_key,
        "payload": some_bldg_payload,
        "processed": False,
        "occupied": False,
        "occupiedBy": None
    })
    def fin():
        print ("teardown bldg")
        db.buildings.remove({"address": some_bldg_address})
    request.addfinalizer(fin)
    return _id
