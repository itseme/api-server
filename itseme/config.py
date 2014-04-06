from os import environ


class Config(object):
    DEBUG = False

    COUCHDB_SERVER = ""
    COUCHDB_DATABASE = ""

    REQUEST_THROTTLE = 10
    REQUEST_THROTTLE_SECONDS = 1

    ## CELERY CONFIG
    BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Berlin'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ENABLE_UTC = True

    ## EMAIL config
    MAIL_SERVER = environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(environ.get("MAIL_PORT", 25))
    MAIL_USERNAME = environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER", "")

    # Twilio for SMS/Phone support
    TWILIO_SID = environ.get("TWILIO_SID", "")
    TWILIO_TOKEN = environ.get("TWILIO_TOKEN", "")
    TWILIO_TOKEN = environ.get("TWILIO_FROM", "")

    # Twitter login
    TWITTER_CONSUMER_KEY = environ.get("TWITTER_CONSUMER_KEY", "")
    TWITTER_CONSUMER_SECRET = environ.get("TWITTER_CONSUMER_SECRET", "")

    # Facebook login
    FACEBOOK_CONSUMER_KEY = environ.get("FACEBOOK_CONSUMER_KEY", "")
    FACEBOOK_CONSUMER_SECRET = environ.get("FACEBOOK_CONSUMER_SECRET", "")

    # GITHUB login
    GITHUB_CONSUMER_KEY = environ.get("GITHUB_CONSUMER_KEY", "")
    GITHUB_CONSUMER_SECRET = environ.get("GITHUB_CONSUMER_SECRET", "")




class ProductionConfig(Config):
    REDIS_APP_CACHE = "redis://localhost:6379/0"
    BROKER_URL = "redis://{0}:{1}/1".format(
                environ.get("REDIS_PORT_6379_TCP_ADDR", ""),
                environ.get("REDIS_PORT_6379_TCP_PORT", "")
                )
    CELERY_RESULT_BACKEND = "redis://{0}:{1}/2".format(
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
    REQUEST_THROTTLE = 10000
    REDIS_APP_CACHE = "redis://localhost:6379/0"
    BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

    TWILIO_FROM = "+15005550006"
    TWILIO_SID = "ACed8a47da452b063795e2cb3a5dba0b4d"
    TWILIO_TOKEN = environ.get("TWILIO_DEBUG_TOKEN", "")

    DEBUG = True


class TestConfig(Config):
    SECRET_KEY = "TESTING"
    BROKER_BACKEND = 'memory'
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_ALWAYS_EAGER = True
    DEBUG = True
    TESTING = True

    MAIL_DEFAULT_SENDER  = "mickey@example.com"
