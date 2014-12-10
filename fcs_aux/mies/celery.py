from __future__ import absolute_import
from celery import Celery


app = Celery('mies',
             include=[
                 'mies.data_pipes.twitter_social_feed.pipe',
                 'mies.buildings.model',
             ])

app.config_from_object('mies.celeryconfig')
