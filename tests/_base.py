
from itseme import app
from itseme import tasks

import yaml


def load_db():
    return yaml.load(open("tests/test_data.yml"))


class BaseTestMixin(object):

    def setUp(self):
        app.app.config.from_object("itseme.config.TestConfig")
        self.database = load_db()
        app._get_db = lambda: self.database
        tasks.celery.conf.update(app.app.config)
        tasks.mail.init_app(app.app)
