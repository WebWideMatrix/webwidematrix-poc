import pytest

from mies.buildings.model import build_bldg_address
from mies.buildings.model import is_vacant
from mies.buildings.model import find_spot
from mies.buildings.constants import FLOOR_W, FLOOR_H, PROXIMITY


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
    assert True == is_vacant("g-b(1,2)")


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
    address, x, y = find_spot(flr, near_x=near_x, near_y=near_y)
    assert address is not None
    assert address == "{flr}-b({x},{y})".format(**locals())
    assert 0 <= x <= FLOOR_W
    assert 0 <= y <= FLOOR_H
    assert abs(x - near_x) <= PROXIMITY
    assert abs(y - near_y) <= PROXIMITY
