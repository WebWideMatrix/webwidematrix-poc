from mies.buildings.model import build_bldg_address


def test_build_ground_level_bldg_address():
    flr = "g"
    x = 123
    y = 456
    expected = "g-b(123,456)"
    got = build_bldg_address(flr, x, y)
    assert got == expected


def test_build_upper_level_bldg_address():
    flr = "g-b(1,2)-l0"
    x = 123
    y = 456
    expected = "g-b(1,2)-l0-b(123,456)"
    got = build_bldg_address(flr, x, y)
    assert got == expected
