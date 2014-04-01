
from flask import Flask, jsonify, g
from celery import Celery

import config
import couchdb

app = Flask(__name__)


def _get_db():
    return app.couch[app.config["COUCHDB_SERVER"]]


@app.before_first_request
def setup_couch():
    if app.config["TESTING"]:
        return
    app.couch = couchdb.Server(app.config["COUCHDB_SERVER"])
    if app.config["COUCHDB_SERVER"] not in app.couch:
        app.couch.create(app.config["COUCHDB_SERVER"])


@app.before_request
def connect_db():
    g.couch = _get_db()


@app.route("/v1/register")
def register():
    return jsonify({})


@app.route("/v1/confirm/<string:hashkey>/<string:target>")
def confirm_one(hashkey, target):
    try:
        doc = g.couch[hashkey]
        return jsonify({"confirmed": doc["status"] == "confirmed" and doc["target"] == target.strip()})
    except KeyError:
        return jsonify({"confirmed": False})


@app.route("/v1/confirm")
def confirm_many():
    return jsonify({})


@app.route('/')
def hello_world():
    return 'Hello World!'


def setup_db():
    db_manager = CouchDBManager(auto_sync=False)
    db_manager.setup(app)
    #db_manager.sync(app)


def setup_app():
    app.celery = Celery('tasks')
    app.celery.config.update(app.config)
    setup_db()


if __name__ == '__main__':
    app.config.from_object("config.DebugConfig")
    setup_app()
    app.run(debug=config.DEBUG)