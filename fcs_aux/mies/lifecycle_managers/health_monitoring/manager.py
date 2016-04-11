import logging
import datetime

from mies.celery import app
from mies.lifecycle_managers.daily_building.manager import _build_user_current_bldg_cache_key
from mies.mongo_config import get_db
from mies.redis_config import get_cache


COVERAGE_CACHE_KEY = "metrics.coverage"
INGRESS_VS_EGRESS_CACHE_KEY = "metrics.ingress_vs_egress"

PERIOD = 30


def measure_coverage(db, cache):
    results = []
    users = db.users.find()
    # TODO read & process in batches
    for user in users:
        todays_bldg_addr = cache.get(_build_user_current_bldg_cache_key(user["_id"]))
        flr = "{}-l0".format(todays_bldg_addr)
        processed = db.buildings.find({
            "flr": flr,
            "processed": True
        }).count()
        total = db.buildings.find({
            "flr": flr
        }).count()
        if not total:
            return 0
        else:
            results.append(float(processed) / float(total))
    if results:
        return float(sum(results)) / float(len(results))
    return 0


def measure_ingress_vs_egress(db, cache):
    results = []
    users = db.users.find()
    start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=PERIOD)
    # TODO read & process in batches
    for user in users:
        todays_bldg_addr = cache.get(_build_user_current_bldg_cache_key(user["_id"]))
        in_flr = "{}-l0".format(todays_bldg_addr)
        ingress = db.buildings.find({
            "flr": in_flr,
            "createdAt": {"$gte": start_time}
        }).count()
        out_flr = "{}-l1".format(todays_bldg_addr)
        egress = db.buildings.find({
            "flr": out_flr,
            "createdAt": {"$gte": start_time}
        }).count()
        results.append(ingress - egress)
    if results:
        return float(sum(results)) / float(len(results))
    return 0


def log_metrics(metrics, results):
    logging.info("#"*80)
    logging.info("#"*80)
    logging.info("#"*80)
    logging.info("####")
    logging.info("####")
    logging.info("####")
    for i, m in enumerate(metrics):
        logging.info("####\t{label}:\t\t{result}".format(label=m["label"],
                                                         result=results[i]))
    logging.info("####")
    logging.info("####")
    logging.info("####")
    logging.info("#"*80)
    logging.info("#"*80)
    logging.info("#"*80)


@app.task(ignore_result=True)
def invoke():
    """
    Measures several health metrics:
    * Coverage: Loops over all users, gets their current bldg, & measures the % of processed bldgs.
    * Ingress vs. Egress: Average delta between new buildings in l0 & new buildings in l1, during
        the last 30 minutes
    """
    logging.info("Invoking daily-bldg lifecycle manager...")
    db = get_db()
    cache = get_cache()

    metrics = [
        dict(label="Coverage", func=measure_coverage,
             cache_key=COVERAGE_CACHE_KEY),
        dict(label="Ingress vs. Egress", func=measure_ingress_vs_egress,
             cache_key=INGRESS_VS_EGRESS_CACHE_KEY),
    ]

    results = []
    for m in metrics:
        metric_result = m["func"](db, cache)
        results.append(metric_result)
        cache.lpush(m["cache_key"], (datetime.datetime.utcnow(), metric_result))

    log_metrics(metrics, results)
