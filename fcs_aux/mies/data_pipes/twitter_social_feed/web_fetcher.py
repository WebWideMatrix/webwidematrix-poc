from twitter import *

from mies.buildings.model import create_buildings
from mies.twitterconfig import CONSUMER_KEY, CONSUMER_SECRET


def extract_payload_from_post(post):
    result = {
        ""
    }
    return result


def invoke_data_pipes(page):
    """
    Receives a page of data-pipes.
    Invokes the Twitter API to fetch the home-timeline per each data-pipe.
    Send the received results to the buildings-creator task
    :param page:
    """
    # TODO send to an async web-fetcher service (Tornado)
    for dp in page:
        auth = OAuth(token=dp.tokens.accessToken,
                     token_secret=dp.tokens.accessTokenSecret,
                     consumer_key=CONSUMER_KEY,
                     consumer_secret=CONSUMER_SECRET)
        t = Twitter(auth=auth)
        args = {"count": 200}
        if dp.latestId:
            args["since_id"] = dp.latestId
        results = t.statuses.home_timeline(**args)
        buildings = []
        for post in results:
            buildings.append(extract_payload_from_post(post))
        to_create = {
            "buildings": buildings,
            "flr": dp.connectedBldg
        }
        create_buildings.delay(**to_create)
