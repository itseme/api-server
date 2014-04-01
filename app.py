from flask import Flask, jsonify
from flaskext.couchdb import CouchDBManager
from celery import Celery

import config

app = Flask(__name__)


@app.route("/v1/register")
def register():
    return jsonify({})


@app.route("/v1/confirm")
def confirm():
    return jsonify({})


@app.route('/')
def hello_world():
    return 'Hello World!'


def setup_app():
    app.celery = Celery('tasks', broker=config.celery_broker)
    db_manager = CouchDBManager(auto_sync=False)
    manager.setup(app)


if __name__ == '__main__':
    setup_app()
    app.run()