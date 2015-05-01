from datetime import datetime
from mock import patch
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


def test_choose_action():
    bldg = {
        "contentType": "twitter-social-post"
    }
    resident = Resident({})
    expected = "fetch-article"
    got = resident.choose_action(bldg)
    assert got == expected


def test_mark_as_executing():
    resident = Resident({})
    bldg = {
    }
    action_status = {
        "startedAt": datetime.now()
    }
    with patch("mies.residents.acting.flow.add_new_action_status") as add_status_mock:
        resident.mark_as_executing("fetch-article", bldg)
        add_status_mock.assert_called_once_with()



def test_start_action():
    pass
