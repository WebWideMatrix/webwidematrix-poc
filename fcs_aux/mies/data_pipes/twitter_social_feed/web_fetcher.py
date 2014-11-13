import logging
from twitter import *

from mies.buildings.model import create_buildings
from mies.twitterconfig import CONSUMER_KEY, CONSUMER_SECRET, TWITTER_POSTS_LIMIT
from mies.data_pipes.twitter_social_feed import TWITTER_SOCIAL_POST


def extract_payload_from_post(post):
    payload = {
        "text": post.get("text"),
        "language": post.get("lang"),
        "external_id": post.get("id"),
        "created_at": post.get("id"),
        "in_reply_to_id": post.get("in_reply_to_status_id"),
        "in_reply_to_screen_name": post.get("in_reply_to_screen_name"),
        "favorite_count": post.get("favorite_count"),
        "reshare_count": post.get("retweet_count"),
        "source": post.get("source"),
        "reshared": post.get("retweeted"),
        "possibly_sensitive": post.get("possibly_sensitive"),
        "user": {
            "name": post.get("user").get("name"),
            "screen_name": post.get("user").get("screen_name"),
            "external_id": post.get("user").get("id"),
            "description": post.get("user").get("description"),
            "language": post.get("user").get("lang"),
            "url": post.get("user").get("url"),
            "number_of_posts": post.get("user").get("statuses_count"),
            "number_of_followers": post.get("user").get("followers_count"),
        },
        "financial_symbols": post.get("entities").get("symbols"),
        "user_mentions": post.get("entities").get("user_mentions"),
        "hashtags": post.get("entities").get("hashtags"),
        "urls": post.get("entities").get("urls"),
    }
    return payload


def invoke_data_pipes(page):
    """
    Receives a page of data-pipes.
    Invokes the Twitter API to fetch the home-timeline per each data-pipe.
    Send the received results to the buildings-creator task
    :param page: batch of data-pipe objects read from the database.
    """
    # TODO send to an async web-fetcher service (Tornado)
    count = 0
    for dp in page:
        auth = OAuth(token=dp["tokens"]["accessToken"],
                     token_secret=dp["tokens"]["accessTokenSecret"],
                     consumer_key=CONSUMER_KEY,
                     consumer_secret=CONSUMER_SECRET)
        t = Twitter(auth=auth)
        args = {"count": TWITTER_POSTS_LIMIT}
        latest_id = dp["latestId"]
        done = False
        while not done:
            if latest_id is not None:
                args["since_id"] = latest_id
            results = t.statuses.home_timeline(**args)
            done = len(results) < TWITTER_POSTS_LIMIT
            payloads = []
            for post in results:
                payloads.append(extract_payload_from_post(post))
                latest_id = post.get("id")
                count += 1
            # TODO check whether the connected bldg is a flr or a bldg
            target_flr = dp["connectedBldg"] + "-l0"
            logging.info("Sending {} buildings..".format(len(payloads)))
            create_buildings.s(content_type=TWITTER_SOCIAL_POST,
                               payloads=payloads, flr=target_flr)\
                .apply_async(queue="create_buildings")
    return count