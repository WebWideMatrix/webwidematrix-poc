from collections import namedtuple
import pytest


@pytest.fixture()
def data_pipes_batch():
    return [
        {
            "_id": "PXTwtAZeFxHs5WX43", "connectedBldg": "g-b(92,91)",
            "frequency": None,
            "latestId": 520403936117927936, "schedule": {"minutes_offset": 8},
            "status": "active",
            "tokens": {"accessToken": "fake",
                       "accessTokenSecret": "fake"},
            "type": "PersonalTwitterFeed"
        }
    ]


@pytest.fixture()
def home_timeline_response():
    Post = namedtuple('Post', 'id text lang created_at in_reply_to_status_id '
                              'in_reply_to_screen_name favorite_count '
                              'retweet_count retweeted source entities '
                              'user')
    Url = namedtuple('Url', 'url indices expanded_url display_url')
    User = namedtuple('User', 'name screen_name id description lang '
                              'url statuses_count followers_count '
                              'profile_text_color profile_background_color '
                              'profile_link_color')
    resp = [
        Post(text="Radio 1 launches content for iPlayer http://t.co/rU5SgUXouX",
             id=531722559625396224,
             lang="en",
             created_at="Wed Jan 10 12:41:22 +0000 2007",
             in_reply_to_status_id=None,
             in_reply_to_screen_name=None,
             favorite_count=32,
             retweet_count=18,
             retweeted=True,
             source="<a href=http://www.socialflow.com rel=nofollow>SocialFlow</a>",
             entities={
                 "symbols": [],
                 "user_mentions": [],
                 "hashtags": [],
                 "urls": [
                     Url(url="http://t.co/rU5SgUXouX",
                         indices=(37, 59),
                         expanded_url="http://bbc.in/1yoNRnE",
                         display_url="bbc.in/1yoNRnE")
                 ]
             },
             user=User(id=621583, name="BBC Technology",
                       screen_name="BBCTech", lang="en",
                       url="http://t.co/xBkUyADpLc",
                       statuses_count=16577,
                       followers_count=331992,
                       profile_text_color="white",
                       profile_background_color="black",
                       profile_link_color="blue",
                       description="The official account for the BBC technology news team."),
             ),
        Post(text="Your gang's done gone away.",
             id=531722559625399350,
             lang="en",
             created_at="Wed Jan 10 12:41:23 +0000 2007",
             in_reply_to_status_id=None,
             in_reply_to_screen_name=None,
             favorite_count=0,
             retweet_count=1,
             retweeted=False,
             source="<a href=http://www.socialflow.com rel=nofollow>SocialFlow</a>",
             entities={
                 "symbols": [],
                 "user_mentions": [],
                 "hashtags": [],
                 "urls": []
             },
             user=User(id=2368723, name="Kurt Vonnegut",
                       screen_name="ice9", lang="en",
                       url="http://vonnegut.com",
                       statuses_count=4513,
                       followers_count=12876283,
                       description="An author",
                       profile_text_color="black",
                       profile_background_color="white",
                       profile_link_color="blue"),
             )
    ]
    return resp
