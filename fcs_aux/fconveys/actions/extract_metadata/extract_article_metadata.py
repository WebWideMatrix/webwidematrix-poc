import logging
from schemato import Schemato
from schemato.distillery import ParselyDistiller, NewsDistiller

from mies.celery import app


@app.task(name='extract-article-metadata')
def extract_article_metadata_action(input_payload):
    logging.info("Extracting article metadata")
    logging.info(input_payload)
    assert "url" in input_payload
    url = input_payload.get("url")
    result_payloads = []

    logging.info("text in raw? {}".format("text" in input_payload))
    article = Schemato(input_payload.get("text"))
    metadata = None
    d1 = ParselyDistiller(article)
    try:
        metadata = d1.distill()
    except AttributeError:
        logging.exception("ParselyDistiller failed to extract metadata from: {}".format(url))
        try:
            d2 = NewsDistiller(article)
            metadata = d2.distill()
        except AttributeError:
            logging.exception("NewsDistiller failed to extract metadata from: {}".format(url))
    if not metadata:
        # nothing found :(
        return []

    result_payloads.append(
        {
            "contentType": "article-with-metadata",
            "key": url,
            "summary": metadata,
            "placement_hints": {
                "new_bldg": False,
            }
        }
    )

    return result_payloads
