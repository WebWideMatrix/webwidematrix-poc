import pytest
from mies.buildings.utils import (get_flr, get_bldg,
                                  get_containing_bldg_address,
                                  extract_bldg_coordinates, replace_bldg_coordinates)


def test_get_flr():
    addr = "g-b(1,2)-l2-b(3,4)"
    expected = "g-b(1,2)-l2"
    got = get_flr(addr)
    assert got == expected


def test_get_bldg():
    addr = "g-b(1,2)-l2-b(3,4)-l0"
    expected = "g-b(1,2)-l2-b(3,4)"
    got = get_bldg(addr)
    assert got == expected


def test_get_containing_bldg_address():
    addr = "g-b(1,2)-l2-b(3,4)"
    expected = "g-b(1,2)"
    got = get_containing_bldg_address(addr)
    assert got == expected


def test_extract_bldg_coordinates():
    addr = "g-b(1,2)-l2-b(3,4)"
    expected = (3, 4)
    got = extract_bldg_coordinates(addr)
    assert got == expected

@pytest.mark.parametrize("addr, x, y, expected_result",
    [
        ("g", 12, 17, "g"),
        ("g-b(1,2)", 12, 17, "g-b(12,17)"),
        ("g-b(1,2)-l0", 12, 17, "g-b(12,17)-l0"),
        ("g-b(1,2)-l2-b(3,4)", 12, 17, "g-b(1,2)-l2-b(12,17)"),
        ("g-b(1,2)-l2-b(3,4)-l0", 12, 17, "g-b(1,2)-l2-b(12,17)-l0"),
    ])
def test_replace_bldg_coordinates(addr, x, y, expected_result):
    assert replace_bldg_coordinates(addr, x, y) == expected_result
