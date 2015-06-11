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

    article = Schemato(url)

    d1 = ParselyDistiller(article)
    try:
        metadata = d1.distill()
    except AttributeError:
        d2 = NewsDistiller(article)
        metadata = d2.distill()
    if not metadata:
        # nothing found :(
        return []

    result_payloads.append(
        {
            "content_type": "article-with-metadata",
            "key": url,
            "payload": metadata,
            "placement_hints": {
                "new_bldg": False,
            }
        }
    )

    return result_payloads
