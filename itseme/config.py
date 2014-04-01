
class Config(object):
    DEBUG = True

    COUCHDB_SERVER = ""
    COUCHDB_DATABASE = ""

    ## CELERY CONFIG
    BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = 'amqp://'

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Berlin'
    CELERY_ENABLE_UTC = True


class DebugConfig(Config):
    pass


class TestConfig(Config):
    TESTING = True
