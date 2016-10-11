from mies.residents.model import Resident


def test_creating_resident_object(resident_data):
    res = Resident(resident_data)
    assert res is not None
    assert "name" in res
    assert res["name"] == resident_data["name"]
    assert res.name == res["name"]
