from celery.utils.log import get_task_logger
from mies.celery import app

logging = get_task_logger(__name__)


@app.task(name='fetch-article')
def fetch_article_action(input_payload):
    logging.info("Fetching article from social post")
    logging.info(input_payload)

    result_payloads = []
    for link in input_payload["urls"]:
        url = link.expanded_url
        display_url = link.display_url
        shortened_url = link.url

        # TODO perform a GET request to fetch the link file

        # TODO save the result into a temp file

        # TODO parse the file with textract

        # TODO delete the file

        # TODO append the parsed article text
        result_payloads.append(
            {
                "content_type": "article-text",
                "key": url,
                "payload": {
                    "url": url,
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
        )

    return result_payloads

