import logging
from mies.celery import app


@app.task(ignore_result=True)
def invoke():
    """
    Loops over all users and:
    * Looks up an existing bldg for the current date
    * If not found, creates one, next to the previous day
    * Connects any data-pipes for this user to the created bldg
    """
    logging.info("Invoking lifecycle manager...")
