from __future__ import unicode_literals
import json
import os

from goose import Goose


"""
We want to experiment with training a fastText classifier model
using tagged web urls dataset (obtained from delicious).

The dataset was obtained from: https://arvindn.livejournal.com/116137.html

To do that, we need to create an examples file in the format:
__label__L1 __label__L2 [...] text of the web page

"""

INPUT_FILE = "/Users/udi/Downloads/delicious-rss-1250k"
OUTPUT_FILE = "tagged_web_pages.train"

OFFSET = 88677
BATCH_SIZE = 100000

MAX_ARTICLE_SIZE = 1000


def read_dataset(offset=OFFSET, batch_size=BATCH_SIZE):
    i = 0
    count = 0
    with open(INPUT_FILE) as src:
        for l in src:
            i += 1
            if i < OFFSET:
                continue
            count += 1
            data = json.loads(l)
            # should filter?
            if not data.get("tags"):
                continue
            # web page attributes
            link = data.get("link")
            title = data.get("title")
            tags = [t.get("term") for t in data.get("tags")]

            yield (i, link, title, tags)

            if count > BATCH_SIZE:
                break


def fetch_web_page_text(url, title):
    g = Goose()
    article = g.extract(url=url)
    title = article.title
    metadata = article.meta_description
    text = article.cleaned_text[:1000]
    combined = "{} {} {}".format(title, metadata, text)
    if (title or metadata or text) is None:
        return None
    if len(combined) == 2:
        return None
    if "\n" in combined:
        combined = combined.replace("\n", " ")
    return combined


def add_example(tags, text):
    with open(OUTPUT_FILE, "a") as f:
        line = " ".join(["__label__{}".format(t) for t in tags])
        line = "{} {}\n".format(line, text)
        f.write(line.encode('utf8'))


if __name__ == "__main__":
    for i, link, title, tags in read_dataset():
        print "_"*100
        print "Processing web page === {} === ({})".format(i, title)
        try:
            text = fetch_web_page_text(link, title)
        except Exception, e:
            print "Got exception: {}, skipping".format(e)
            text = None
        if text:
            chars = len(text)
            print "\tAdding example ({} chars) with labels: {}".format(chars, tags)
            add_example(tags, text)
        else:
            print "\tCouldn't fetch web page text"
