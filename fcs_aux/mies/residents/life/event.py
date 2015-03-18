from celery.utils.log import get_task_logger
from mies.celery import app

logging = get_task_logger(__name__)


@app.task(ignore_result=True)
def handle_life_event(resident):
    logging.info("Resident {id} life event invoked..."
                 .format(id=resident["_id"]))
