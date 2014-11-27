import logging
import tweepy

from mies.buildings.model import create_buildings
from mies.twitterconfig import CONSUMER_KEY, CONSUMER_SECRET, TWITTER_POSTS_LIMIT
from mies.data_pipes.twitter_social_feed import TWITTER_SOCIAL_POST
from mies.data_pipes.model import update_data_pipe


def extract_payload_from_post(post):
    payload = {
        "text": post.text,
        "language": post.lang,
        "external_id": post.id,
        "created_at": post.id,
        "in_reply_to_id": post.in_reply_to_status_id,
        "in_reply_to_screen_name": post.in_reply_to_screen_name,
        "favorite_count": post.favorite_count,
        "reshare_count": post.retweet_count,
        "source": post.source,
        "reshared": post.retweeted,
        "user": {
            "name": post.user.name,
            "screen_name": post.user.screen_name,
            "external_id": post.user.id,
            "description": post.user.description,
            "language": post.user.lang,
            "url": post.user.url,
            "number_of_posts": post.user.statuses_count,
            "number_of_followers": post.user.followers_count,
        },
        "financial_symbols": post.entities.get("symbols"),
        "user_mentions": post.entities.get("user_mentions"),
        "hashtags": post.entities.get("hashtags"),
        "urls": post.entities.get("urls"),
    }
    return payload


def pull_from_data_pipes(page):
    """
    Receives a page of data-pipes.
    Invokes the Twitter API to fetch the home-timeline per each data-pipe.
    Send the received results to the buildings-creator task
    :param page: batch of data-pipe objects read from the database.
    """
    # TODO send to an async web-fetcher service (Tornado)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    count = 0
    for dp in page:
        auth.set_access_token(dp["tokens"]["accessToken"], dp["tokens"]["accessTokenSecret"])
        t = tweepy.API(auth)
        args = {"count": TWITTER_POSTS_LIMIT}
        latest_id = dp.get("latestId")
        new_latest_id = None
        max_id = None
        done = False
        batch_count = 0
        while not done:
            payloads = []
            batch_count += 1
            if latest_id is not None:
                args["since_id"] = latest_id
            if max_id is not None:
                args["max_id"] = max_id - 1
            logging.info("Invoking twitter API with args: {}".format(args))
            results = t.home_timeline(**args)
            if not results:
                done = True
            else:
                for post in results:
                    if latest_id is not None and post.id <= latest_id:
                        done = True
                    elif new_latest_id is None or post.id > new_latest_id:
                        new_latest_id = post.id
                    if not done:
                        max_id = post.id
                        payloads.append(extract_payload_from_post(post))
                        count += 1
                if latest_id is None and new_latest_id is not None:
                    done = True

            if payloads:
                # TODO check whether the connected bldg is a flr or a bldg
                target_flr = dp["connectedBldg"] + "-l0"
                logging.info("Sending {} buildings to {}..".format(len(payloads), target_flr))
                create_buildings.s(content_type=TWITTER_SOCIAL_POST,
                                   payloads=payloads, flr=target_flr)\
                    .apply_async()
                if new_latest_id is not None:
                    update_data_pipe(dp["_id"], {"latestId": new_latest_id})
    return count