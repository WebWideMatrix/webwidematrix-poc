from celery.utils.log import get_task_logger
from mies.celery import app
from mies.data_pipes.model import STATUS_ACTIVE
from mies.residents.life.event import handle_life_event
from mies.residents.model import load_residents

logging = get_task_logger(__name__)


@app.task(ignore_result=True)
def invoke():
    """
    Invoke a life event for all residents
    :return:
    """
    criteria = {
        "status": STATUS_ACTIVE
    }
    for page in load_residents(criteria):
        logging.info(" - "*100)
        for resident in page:
            logging.info(" | "*100)
            logging.info(type(resident))
            logging.info(resident)
            handle_life_event.s(resident).apply_async(queue='life_events', routing_key='life.events')
