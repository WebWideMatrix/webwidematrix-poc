from mock import patch, call, ANY
from mies.data_pipes.twitter_social_feed import TWITTER_SOCIAL_POST
from mies.data_pipes.twitter_social_feed.web_fetcher import pull_from_data_pipes


@patch('mies.data_pipes.twitter_social_feed.web_fetcher.update_data_pipe')
@patch('mies.data_pipes.twitter_social_feed.web_fetcher.create_buildings.s')
def test_pull_from_data_pipes(create_bldgs, update_pipe, data_pipes_batch,
                              home_timeline_response):
    api_results = [home_timeline_response, []]
    with patch('mies.data_pipes.twitter_social_feed.web_fetcher.tweepy.API.home_timeline',
               side_effect=api_results):
        pull_from_data_pipes(data_pipes_batch)
    assert create_bldgs.call_count == 1
    target_flr = data_pipes_batch[0]["connectedBldg"] + "-l0"
    keys = [p.id for p in home_timeline_response]
    create_bldgs.assert_has_calls([
        call(TWITTER_SOCIAL_POST, keys, ANY, target_flr),
        call().apply_async()])
    update_pipe.assert_called_once_with(data_pipes_batch[0]["_id"],
                                        {'latestId': home_timeline_response[1].id})
