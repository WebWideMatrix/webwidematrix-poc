from mock import patch

from mies.data_pipes.model import load_data_pipes


@patch('mies.data_pipes.model.MongoClient')
def test_load_data_pipes(mongo_client):
    mc = mongo_client.return_value
    data_pipe_spec = {'status': 'active', 'connectedBldg': {'$exists': True}}
    for page in load_data_pipes():
        mc.meteor.data_pipes.find.assert_called_once_with(data_pipe_spec, skip=0, limit=100)
