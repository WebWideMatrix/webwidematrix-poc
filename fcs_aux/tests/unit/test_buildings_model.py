from mies.buildings.model import build_bldg_address


def test_build_bldg_address():
    expected = "g-b(12,3)-l2-b(23,456)"
    got = build_bldg_address("g-b(12,3)-l2", 23, 456)
    assert got == expected
