fcs-skateboard
==============

social feed visualizations

To run:
-------

redis: redis-server

meteor: env REDIS_CONFIGURE_KEYSPACE_NOTIFICATIONS=1 meteor

celery: celery -A mies worker -l info -B

