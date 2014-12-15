from datetime import datetime
from mock import patch, MagicMock
import pytest

from mies.buildings.model import build_bldg_address
from mies.buildings.model import is_vacant
from mies.buildings.model import find_spot
from mies.buildings.constants import FLOOR_W, FLOOR_H, PROXIMITY
from mies.buildings.model import construct_bldg, create_buildings


@pytest.mark.parametrize("flr,x,y,address", [
    ("g", 1, 2, "g-b(1,2)"),
    ("g", 12, 3, "g-b(12,3)"),
    ("g", 123, 456, "g-b(123,456)")])
def test_build_ground_level_bldg_address(flr, x, y, address):
    got = build_bldg_address(flr, x, y)
    assert got == address

@pytest.mark.parametrize("flr,x,y,address", [
    ("g-b(1,2)-l0", 1, 2, "g-b(1,2)-l0-b(1,2)"),
    ("g-b(1,2)-l0-b(3,4)-l1", 1, 2, "g-b(1,2)-l0-b(3,4)-l1-b(1,2)"),
    ("g-b(1,2)-l3", 123, 456, "g-b(1,2)-l3-b(123,456)")])
def test_build_upper_level_bldg_address(flr, x, y, address):
    got = build_bldg_address(flr, x, y)
    assert got == address


def test_is_vacant():
    db = MagicMock()
    db.buildings.find_one = MagicMock(return_value=None)
    assert True == is_vacant("g-b(1,2)", db)
    db.buildings.find_one.assert_called_once_with({'address': 'g-b(1,2)'})


def test_find_spot():
    flr = "g-b(1,2)-l1"
    state = {}
    address, x, y = find_spot(flr, state)
    assert address is not None
    assert address == "{flr}-b({x},{y})".format(**locals())
    assert 0 <= x <= FLOOR_W
    assert 0 <= y <= FLOOR_H


def test_find_spot_near():
    flr = "g-b(1,2)-l1"
    near_x = 12
    near_y = 34
    pos_hints = {
        "near_x": near_x,
        "near_y": near_y
    }
    address, x, y = find_spot(flr, position_hints=pos_hints)
    assert address is not None
    assert address == "{flr}-b({x},{y})".format(**locals())
    assert 0 <= x <= FLOOR_W
    assert 0 <= y <= FLOOR_H
    assert abs(x - near_x) <= PROXIMITY
    assert abs(y - near_y) <= PROXIMITY


def test_construct_bldg():
    flr = "g-b(1,2)-l1"
    near_x = 75
    near_y = 6
    pos_hints = {
        "near_x": near_x,
        "near_y": near_y
    }
    content_type = "SomeContent"
    payload = {
        "field1": "value 1",
        "field2": "value 2",
        "field3": "value 3",
    }
    db = MagicMock()
    db.buildings.find_one = MagicMock(return_value=None)
    got = construct_bldg(flr, content_type, "key", payload,
                         position_hints=pos_hints, db=db)
    assert got is not None
    assert got['address'].startswith(flr)
    assert got['flr'] == flr
    assert abs(got['x'] - near_x) <= PROXIMITY
    assert abs(got['y'] - near_y) <= PROXIMITY
    assert (datetime.utcnow() - got['createdAt']).seconds < 10
    assert got['payload'] == payload
    assert not got['processed']
    assert not got['occupied']
    assert got['occupiedBy'] is None


@patch('mies.buildings.model.MongoClient')
def test_create_buildings(mongo_client):
    db = MagicMock()
    db.buildings.find_one = MagicMock(return_value=None)
    db.buildings.insert = MagicMock(return_value=None)
    cl = MagicMock()
    cl.meteor = db
    mongo_client.return_value = cl

    content_type = "SomeContent"
    nbuildings = 35
    keys = ["key-{}".format(i) for i in xrange(nbuildings)]
    payloads = [
        {
            "field1": "value 1.1",
            "field2": "value 1.2",
            "field3": "value 1.3",
        },
    ]* nbuildings
    flr = "g-b(1,2)-l1"
    got = create_buildings(content_type, keys, payloads, flr)
    assert len(got) == nbuildings
    assert db.buildings.insert.call_count == 4  # 4 batch inserts
