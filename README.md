fcs-skateboard
==============

social feed visualizations

To run:
-------

redis: redis-server

meteor: env REDIS_CONFIGURE_KEYSPACE_NOTIFICATIONS=1 meteor

workers: celery -A mies worker -l info -B --concurrency=4 -Q default
residents: celery -A mies worker -l info --concurrency=4 -Q life_events
pipes: celery -A mies worker -l info --concurrency=4 -Q data_pipes
bldgs: celery -A mies worker -l info --concurrency=4 -Q bldg_creation
