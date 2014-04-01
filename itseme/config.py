
class Config(object):
    DEBUG = False

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
    SECRET_KEY = "DEBUG"
    DEBUG = True


class TestConfig(Config):
    SECRET_KEY = "TESTING"
    BROKER_BACKEND = 'memory'
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_ALWAYS_EAGER = True
    DEBUG = True
    TESTING = True

    MAIL_DEFAULT_SENDER  = "mickey@example.com"
