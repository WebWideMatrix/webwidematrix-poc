from mies.buildings.model import is_vacant


def test_is_vacant(db, some_bldg_address, create_some_bldg):
    got = is_vacant(some_bldg_address, db)
    assert got is False

    nothing_there = "g-b(67,37)-l4-b(6512,1298)"
    got = is_vacant(nothing_there, db)
    assert got is True
