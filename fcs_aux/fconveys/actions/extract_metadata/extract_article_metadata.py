import logging
from mies.celery import app


@app.task(name='extract-article-metadata')
def extract_article_metadata_action(input_payload):
    logging.info("Extracting article metadata")
    logging.info(input_payload)
    url = input_payload.get("url")

    result_payloads = []

    # TODO extract metadata using Schemato

    result_payloads.append(
        {
            "content_type": "article-with-metadata",
            "key": url,
            "payload": {
                "url": url,
            },
            "placement_hints": {
                "new_bldg": False,
            }
        }
    )

    return result_payloads
