from celery.utils.log import get_task_logger
from mies.celery import app

logging = get_task_logger(__name__)


@app.task(name='fetch-article')
def fetch_article_action(input_payload):
    logging.info("Fetching article from social post")
    logging.info(input_payload)
    # TODO implement & remove dummy result
    result_payloads = [
        {
            "content_type": "article-text",
            "payload": {
                "url": "http://example.org/articles/some.html",
                "text": "This is the article text"
            },
            "placement_hints": {
                "new_bldg": True,
                "same_flr": False,
                "flr_above": True,
                "location_by_index": False,
                "same_location": True,
            }
        }
    ]

