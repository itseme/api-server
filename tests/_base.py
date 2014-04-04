
from itseme import app
from itseme import tasks

from couchdb.http import ResourceNotFound, ResourceConflict

import yaml


class CouchdbDict(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            raise ResourceNotFound(key)

    def __setitem__(self, key, value):
        existing = dict.get(self, key, None)
        if existing and existing["_rev"]:
            if not value.get("_rev", None) or value.get("_rev", None) != existing["_rev"]:
                raise ResourceConflict()
        return dict.__setitem__(self, key, value)


def load_db():
    return CouchdbDict(yaml.load(open("tests/test_data.yml")))


class BaseTestMixin(object):

    def setUp(self):
        app.app.config.from_object("itseme.config.TestConfig")
        self.database = load_db()
        app._get_db = lambda: self.database
        tasks.celery.conf.update(app.app.config)
        tasks.mail.init_app(app.app)
