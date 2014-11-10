import logging
from mies.celery import app


@app.task(ignore_results=True)
def create_buildings(content_type, payloads, flr):
    for payload in payloads:
        # generate random address
        # verify (using the cache) that it's free
        logging.info("Creating building for {}: {}".format(content_type, payload["text"]))
    # use bulk insert to write all buildings to the database
