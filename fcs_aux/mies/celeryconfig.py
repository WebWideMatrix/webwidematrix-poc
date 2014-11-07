from datetime import timedelta

BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'

CELERYBEAT_SCHEDULE = {
    'invoke_data_pipes_every_few_minutes': {
        'task': 'mies.data_pipes.twitter_social_feed.pipe.invoke',
        'schedule': timedelta(minutes=10),

    }
}
