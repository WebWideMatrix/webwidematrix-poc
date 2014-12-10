from mock import patch

from mies.data_pipes.model import load_data_pipes, update_data_pipe


@patch('mies.data_pipes.model.MongoClient')
def test_load_data_pipes(mongo_client):
    mc = mongo_client.return_value
    data_pipe_spec = {'status': 'active', 'connectedBldg': {'$exists': True}}
    for page in load_data_pipes():
        mc.meteor.data_pipes.find.assert_called_once_with(data_pipe_spec, skip=0, limit=100)


@patch('mies.data_pipes.model.MongoClient')
def test_update_data_pipe(mongo_client):
    mc = mongo_client.return_value
    change = {"field1": "value 1"}
    dp_id = 1
    update_data_pipe(dp_id, change)
    mc.meteor.data_pipes.update.assert_called_once_with({'_id': dp_id}, {'$set': change})
