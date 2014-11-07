from __future__ import absolute_import
from celery import Celery

# move to conf
DATA_PIPES_INTERVAL = 10

app = Celery('mies',
             include=[
                 'mies.data_pipes.twitter_social_feed.pipe'
             ])

app.config_from_object('mies.celeryconfig')
