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


def test_is_action_pending():
    resident = Resident({})
    action_status1 = {
        "startedAt": datetime.now()
    }
    assert resident.is_action_pending(action_status1)
    action_status2 = {
        "startedAt": datetime.now(),
        "endedAt": datetime.now()
    }
    assert not resident.is_action_pending(action_status2)
