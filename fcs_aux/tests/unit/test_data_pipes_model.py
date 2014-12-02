from mock import patch, MagicMock

from mies.data_pipes.model import load_data_pipes


@patch('mies.data_pipes.model.MongoClient')
def test_load_data_pipes(mongo_client):
    mongo_client.meteor = MagicMock()
    load_data_pipes()
    print mongo_client.meteor.mock_calls
    assert 1 == 0
