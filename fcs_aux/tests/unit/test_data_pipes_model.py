from mock import patch, MagicMock

from mies.data_pipes.model import load_data_pipes, update_data_pipe


@patch('mies.data_pipes.model.get_db')
def test_load_data_pipes(get_db):
    db = MagicMock()
    get_db.return_value = db
    data_pipe_spec = {'status': 'active', 'connectedBldg': {'$exists': True}}
    for page in load_data_pipes():
        db.data_pipes.find.assert_called_once_with(data_pipe_spec, skip=0, limit=100)


@patch('mies.data_pipes.model.get_db')
def test_update_data_pipe(get_db):
    db = get_db.return_value
    change = {"field1": "value 1"}
    dp_id = 1
    update_data_pipe(dp_id, change)
    db.data_pipes.update.assert_called_once_with({'_id': dp_id}, {'$set': change})
