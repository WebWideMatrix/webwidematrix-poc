from datetime import datetime
from mock import MagicMock, patch, call, ANY
from mies.data_pipes.model import STATUS_ACTIVE
from mies.data_pipes.twitter_social_feed import PERSONAL_TWITTER_FEED
from mies.lifecycle_managers.daily_building.manager import create_daily_bldg, \
    format_date, _create_bldg, invoke

TODAY = "2014-Dec-21"
CREATED_BLDG_ADDRESS = "g-b(12,34)-l0-b(0,67)"


@patch('mies.lifecycle_managers.daily_building.manager.update_data_pipe')
@patch('mies.lifecycle_managers.daily_building.manager.create_buildings',
       return_value=[CREATED_BLDG_ADDRESS])
def test_create_daily_bldg(create_bldgs, update_pipe):
    today = "2014-Dec-18"
    user_bldg_address = "g-b(12,34)"
    data_pipe_id = "dkadhjaskd"
    user_bldg_id = "uiu4y2i3u2y"
    target_flr = user_bldg_address + "-l0"
    db = MagicMock()
    db.data_pipes.find_one.return_value = {
        "_id": data_pipe_id,
        "status": STATUS_ACTIVE,
        "type": PERSONAL_TWITTER_FEED
    }
    db.buildings.find_one.side_effect = [
        {
            "address": user_bldg_address
        },
        None
    ]
    manager = {
        "dataPipe": data_pipe_id,
        "bldg": user_bldg_id
    }
    create_daily_bldg(db, today, manager)
    db.data_pipes.find_one.assert_called_once_with({"_id": data_pipe_id})
    db.buildings.find_one.assert_has_calls([
        call({"_id": user_bldg_id}),
        call({"flr": target_flr, "key": today}),
    ])
    create_bldgs.assert_called_once_with(is_composite=True, content_type='daily-feed',
                                         position_hints={'next_free': True},
                                         keys=[today],
                                         flr=target_flr,
                                         payloads=[{'date': today,
                                                    'data_pipes':
                                                        [PERSONAL_TWITTER_FEED]}])
    update_pipe.assert_called_once_with(data_pipe_id,
                                        {'connectedBldg': CREATED_BLDG_ADDRESS})


def test_format_date():
    d = datetime(2014, 12, 21, 15, 59, 26)
    expected = TODAY
    got = format_date(d)
    assert got == expected


@patch('mies.lifecycle_managers.daily_building.manager.create_buildings')
def test_create_bldg(create_bldgs_task):
    target_flr = "g-b(12,34)-l0"
    today = TODAY
    data_pipe = {
        "type": PERSONAL_TWITTER_FEED
    }
    expected = "{}-b(56,78)".format(target_flr)
    create_bldgs_task.return_value = expected
    got = _create_bldg(target_flr, today, data_pipe)
    create_bldgs_task.assert_called_once_with(
        is_composite=True,
        position_hints={'next_free': True},
        keys=[today],
        flr=target_flr,
        payloads=[
            {
                'date': today,
                'data_pipes': [PERSONAL_TWITTER_FEED]
            }
        ],
        content_type='daily-feed'
    )
    assert got == expected


@patch('mies.lifecycle_managers.daily_building.manager.get_db')
@patch('mies.lifecycle_managers.daily_building.manager.create_daily_bldg')
@patch('mies.lifecycle_managers.daily_building.manager.format_date',
       return_value=TODAY)
def test_invoke(format, create, get_db):
    db = MagicMock()
    managers = [{"_id": "h34gf23h42"}, {"_id": "4eh2873h28"}, ]
    db.lifecycle_managers.find.return_value = managers
    get_db.return_value = db
    invoke()
    create.assert_has_calls([
        call(ANY, TODAY, managers[0]),
        call(ANY, TODAY, managers[1])
    ])
