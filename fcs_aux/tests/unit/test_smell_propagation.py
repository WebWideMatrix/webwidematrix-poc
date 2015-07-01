from mock import patch, MagicMock

@patch('mies.senses.smell.smell_propagator.get_cache')
def test_smell_propagation(get_cache_mock):
    cache = MagicMock()
    get_cache_mock.return_value = cache
