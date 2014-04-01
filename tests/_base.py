import yaml
import unittest
from itseme import app

def load_db():
    return yaml.load(open("tests/test_data.yml"))

class BaseTestMixin(object):

    def setUp(self):
        app.app.config.from_object("itseme.config.TestConfig")
        self.database = load_db()
        app._get_db = lambda: self.database