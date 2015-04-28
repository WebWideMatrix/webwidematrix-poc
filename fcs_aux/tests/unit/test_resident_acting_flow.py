from datetime import datetime
from mies.residents.model import Resident


def test_get_latest_action():
    expected_result = {"result": "DONE"}
    bldg = {
        "actions": [
            {"startedAt": datetime.now(), "result": "DONE"},
            expected_result,
        ]
    }
    resident = Resident({})
    got = resident.get_latest_action(bldg)
    assert got == expected_result
