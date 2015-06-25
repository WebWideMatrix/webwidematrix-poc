import time
from mies.celery import app
from mies.redis_config import get_cache
from mies.senses.smell.smell_source import get_smell_sources

DEFAULT_SMELL_EXPIRY = 5 * 60     # 5 minutes in seconds

SMELL_CACHE_PATTERN = "SMELL_SOURCE_"

CURRENT_SMELLS_POINTER_KEY = "CURRENT_SMELLS"

def build_key(address):
    return SMELL_CACHE_PATTERN + address


@app.task(ignore_result=True)
def invoke():
    cache = get_cache()

    # create a new hset for the current smells
    new_smells_key = "current_smells_{}".format(time.time())

    for source in get_smell_sources():
        # increments the containing bldgs smell

        # draws rectangle around each smell source

        # per each bldg inside it, increments smell according to distance from source
        pass

    # update the pointer to the new smells
    def update_smells_pointer(pipe):
        current_smells_key = pipe.get(CURRENT_SMELLS_POINTER_KEY)
        pipe.set(CURRENT_SMELLS_POINTER_KEY, new_smells_key)
        pipe.delete(current_smells_key)
    cache.transaction(update_smells_pointer, CURRENT_SMELLS_POINTER_KEY)
