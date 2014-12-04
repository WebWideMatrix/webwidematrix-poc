from mock import patch
from mies.data_pipes.twitter_social_feed.pipe import invoke


@patch('mies.data_pipes.twitter_social_feed.pipe.load_data_pipes')
@patch('mies.data_pipes.twitter_social_feed.pipe.web_fetcher')
def test_invoke(fetcher, load_pipes):
    page = [{"_id": 1}, {"_id": 2}]
    load_pipes.return_value = [page]
    invoke()
    fetcher.pull_from_data_pipes.assert_called_once_with(page)
