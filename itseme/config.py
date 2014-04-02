from os import environ


class Config(object):
    DEBUG = False

    COUCHDB_SERVER = ""
    COUCHDB_DATABASE = ""

    ## CELERY CONFIG
    BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Berlin'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ENABLE_UTC = True


class ProductionConfig(Config):
    BROKER_URL = "redis://{0}:{1}/0".format(
                environ.get("REDIS_PORT_6379_TCP_ADDR", ""),
                environ.get("REDIS_PORT_6379_TCP_PORT", "")
                )
    CELERY_RESULT_BACKEND = "redis://{0}:{1}/1".format(
                environ.get("REDIS_PORT_6379_TCP_ADDR", ""),
                environ.get("REDIS_PORT_6379_TCP_PORT", "")
                )

    COUCHDB_SERVER = "http://{0}:{1}/".format(
                environ.get("COUCH_PORT_5984_TCP_ADDR", ""),
                environ.get("COUCH_PORT_5984_TCP_PORT", "")
                )
    COUCHDB_DATABASE = "itseme"


class DebugConfig(Config):
    SECRET_KEY = "DEBUG"
    COUCHDB_SERVER = "http://localhost:5984/"
    COUCHDB_DATABASE = "itseme"

    BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    DEBUG = True


class TestConfig(Config):
    SECRET_KEY = "TESTING"
    BROKER_BACKEND = 'memory'
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_ALWAYS_EAGER = True
    DEBUG = True
    TESTING = True

    MAIL_DEFAULT_SENDER  = "mickey@example.com"
