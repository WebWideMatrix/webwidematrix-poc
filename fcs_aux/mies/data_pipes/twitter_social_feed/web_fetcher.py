import logging
import tweepy

from mies.buildings.model import create_buildings
from mies.twitter_config import CONSUMER_KEY, \
    CONSUMER_SECRET, TWITTER_POSTS_LIMIT
from mies.data_pipes.twitter_social_feed import TWITTER_SOCIAL_POST
from mies.data_pipes.model import update_data_pipe


def extract_raw_payload_from_post(post):
    payload = {
        "external_url": "http://twitter.com/{user}/status/{id}"
        .format(user=post.user.screen_name, id=post.id),
        "text": post.text,
        "language": post.lang,
        "external_id": str(post.id),
        "created_at": post.created_at,
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
            "profile_text_color": post.user.profile_text_color,
            "profile_background_color": post.user.profile_background_color,
            "profile_link_color": post.user.profile_link_color,
        },
        "financial_symbols": post.entities.get("symbols"),
        "user_mentions": post.entities.get("user_mentions"),
        "hashtags": post.entities.get("hashtags"),
        "urls": post.entities.get("urls"),
    }
    return payload


def extract_summary_from_post_raw_payload(raw_paylaod):
    summary = {
        "text": raw_paylaod["text"],
        "created_at": raw_paylaod["created_at"],
        "external_url": raw_paylaod["external_url"],
        "user": {
            "name": raw_paylaod["user"]["name"],
            "screen_name": raw_paylaod["user"]["screen_name"],
            "profile_text_color": raw_paylaod["user"]["profile_text_color"],
            "profile_background_color": raw_paylaod["user"]["profile_background_color"],
        }
    }
    return summary


def extract_result_from_post_raw_payload(raw_paylaod):
    summary = {
        "text": raw_paylaod["text"],
        "external_id": raw_paylaod["external_id"],
        "created_at": raw_paylaod["created_at"],
        "external_url": raw_paylaod["external_url"],
        "in_reply_to_id": raw_paylaod["in_reply_to_id"],
        "in_reply_to_screen_name": raw_paylaod["in_reply_to_screen_name"],
        "favorite_count": raw_paylaod["favorite_count"],
        "reshare_count": raw_paylaod["reshare_count"],
        "user": {
            "name": raw_paylaod["user"]["name"],
            "screen_name": raw_paylaod["user"]["screen_name"],
            "profile_text_color": raw_paylaod["user"]["profile_text_color"],
            "profile_background_color": raw_paylaod["user"]["profile_background_color"],
        },
        "financial_symbols": raw_paylaod["financial_symbols"],
        "user_mentions": raw_paylaod["user_mentions"],
        "hashtags": raw_paylaod["hashtags"],
        "urls": raw_paylaod["urls"],
    }
    return summary


def pull_from_data_pipes(page):
    """
    Receives a page of data-pipes.
    Invokes the Twitter API to fetch the home-timeline per each data-pipe.
    Send the received results to the buildings-creator task
    :param page: batch of data-pipe objects read from the database.
    """
    logging.info("WEB_FETCHER"*10)
    # TODO send to an async web-fetcher service (Tornado)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    count = 0
    for dp in page:
        if dp.get("connectedBldg") is None:
            logging.warning("Data-pipe {} still not connected to anything"
                            .format(dp["_id"]))
            continue
        auth.set_access_token(dp["tokens"]["accessToken"],
                              dp["tokens"]["accessTokenSecret"])
        t = tweepy.API(auth)
        args = {"count": TWITTER_POSTS_LIMIT}
        latest_id = dp.get("latestId")
        new_latest_id = None
        max_id = None
        done = False
        batch_count = 0
        while not done:
            keys = []
            summary_payloads = []
            raw_payloads = []
            result_payloads = []
            batch_count += 1
            if latest_id is not None:
                args["since_id"] = latest_id
            if max_id is not None:
                args["max_id"] = max_id - 1
            logging.info("Invoking twitter API with args: {}".format(args))
            results = t.home_timeline(**args)

            for post in results:
                if latest_id is not None and post.id <= latest_id:
                    done = True
                elif new_latest_id is None or post.id > new_latest_id:
                    new_latest_id = post.id
                if not done:
                    max_id = post.id
                    keys.append(post.id)
                    raw = extract_raw_payload_from_post(post)
                    raw_payloads.append(raw)
                    summary_payloads.append(extract_summary_from_post_raw_payload(raw))
                    result_payloads.append(extract_result_from_post_raw_payload(raw))
                    count += 1
            else:
                done = True

            if latest_id is None and new_latest_id is not None:
                done = True

            if summary_payloads:
                logging.info("P"*100)
                logging.info("Got {} posts".format(len(summary_payloads)))
                logging.info("P"*100)
                # TODO check whether the connected bldg is a flr or a bldg
                target_flr = dp["connectedBldg"] + "-l0"
                logging.info("Sending {} buildings to {}.."
                             .format(len(summary_payloads), target_flr))
                # create_buildings.s(TWITTER_SOCIAL_POST,
                #                    keys, payloads, target_flr) \
                #     .apply_async()
                heads = [{"key": key} for key in keys]
                bodies = [{
                    "summary_payload": summary_payloads[i],
                    "result_payload": result_payloads[i],
                    "raw_payload": raw_payloads[i],
                } for i in xrange(len(summary_payloads))]
                create_buildings(target_flr, TWITTER_SOCIAL_POST, heads, bodies)
                if new_latest_id is not None:
                    update_data_pipe(dp["_id"],
                                     {"latestId": new_latest_id})
    return count
