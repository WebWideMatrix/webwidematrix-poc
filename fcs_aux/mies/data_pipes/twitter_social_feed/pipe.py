from __future__ import absolute_import
import logging

from mies.celery import app
from mies.data_pipes.model import load_data_pipes
from mies.data_pipes.twitter_social_feed import web_fetcher


@app.task(ignore_result=True)
def invoke():
    """
    * Reads in pages all connected & active data-pipes from the DB
    * Each read page of data-pipes is sent to the web_fetcher service
    in a REST call
    """
    logging.info("Invoking data-pipes...")
    count = 0
    for page in load_data_pipes():
        count += web_fetcher.pull_from_data_pipes(page)
    return "{} posts fetched..".format(count)
