from mies.celery import app
from mies.redis_config import get_cache
from mies.senses.smell.smell_source import get_smell_sources

DEFAULT_SMELL_EXPIRY = 5 * 60     # 5 minutes in seconds

SMELL_CACHE_PATTERN = "SMELL_SOURCE_"


def build_key(address):
    return SMELL_CACHE_PATTERN + address


@app.task(ignore_result=True)
def invoke():
    for source in get_smell_sources():
        # increments the containing bldgs smell

        # draws rectangle around each smell source

        # per each bldg inside it, increments smell according to distance from source
        pass
