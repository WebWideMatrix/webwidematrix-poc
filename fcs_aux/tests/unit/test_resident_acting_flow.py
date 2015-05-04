from datetime import datetime
from mock import patch, ANY
from mies.residents.model import Resident


def test_get_latest_action():
    expected_result = {"result": "DONE"}
    bldg = {
        "actions": [
            {"startedAt": datetime.utcnow(), "result": "DONE"},
            expected_result,
        ]
    }
    resident = Resident({})
    got = resident.get_latest_action(bldg)
    assert got == expected_result


def test_is_action_pending():
    resident = Resident({})
    action_status1 = {
        "startedAt": datetime.utcnow()
    }
    assert resident.is_action_pending(action_status1)
    action_status2 = {
        "startedAt": datetime.utcnow(),
        "endedAt": datetime.utcnow()
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
    resident_id = "3j"
    resident = Resident(dict(_id=resident_id))
    bldg = {
    }
    with patch("mies.residents.acting.flow.add_new_action_status") as add_status_mock:
        with patch("mies.residents.acting.flow.ActingBehavior.update_processing_status") \
                as update_processing_mock:
            resident.mark_as_executing("fetch-article", bldg)
            add_status_mock.assert_called_once_with(bldg, ANY)
            action_status = add_status_mock.call_args[0][1]
            assert "startedAt" in action_status
            assert action_status["startedBy"] == resident_id
            assert "action" in action_status
            update_processing_mock.assert_called_once_with(True)


def test_start_action():
    pass
