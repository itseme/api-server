# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, g, Response, request, abort, make_response

from itseme.providers import PROVIDERS
from itseme.util import json_error
from itseme.tasks import celery, mail


import couchdb
import hashlib
import json

app = Flask(__name__)


def _get_db():
    return app.couch[app.config["COUCHDB_SERVER"]]


def _make_key(*args):
    return hashlib.sha512(":".join(args)).hexdigest()


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


@app.route("/v1/verify/<string:hashkey>")
def verify(hashkey):
    try:
        doc = g.couch[hashkey]
        if doc["status"] != "pending":
            return make_response(jsonify(
                {"confirmed": False,
                 "error": {"code": "not_pending",
                           "message": "Hash isn't pending"}}
                ), 403)
    except KeyError:
        return make_response(jsonify(
            {"confirmed": False,
             "error": {"code": "not_found",
                       "message": "Can't find Hash"}}
            ), 404)

    resp = {"confirmed": True}

    provider_return = PROVIDERS[doc["provider"]](app).verify(doc)
    if provider_return:
        if isinstance(provider_return, Response):
            return provider_return
        resp.update(provider_return)

    doc["confirmed"] = True

    for x in ("provider", "provider_id"):
        # we do not want those in here
        try:
            del doc[x]
        except KeyError:
            pass

    # explicitly write it again
    g.couch[hashkey] = doc

    return jsonify(resp)


@app.route("/v1/register/<string:provider>/<string:provider_id>/<string:endpoint>")
def register(provider, provider_id, endpoint):
    endpoint = endpoint.strip()
    if provider != "xmpp" or provider_id != endpoint:
        # let's prove the user is allowed to connect
        try:
            if g.couch[_make_key("xmpp", endpoint)]["status"] != "confirmed":
                abort(401)
        except KeyError:
            abort(401)

    key = _make_key(provider, provider_id)
    doc = {"_id": key, "provider": provider,
           "provider_id": provider_id, "status": "pending",
           "target": endpoint}

    resp = {"status": "pending", "hash": key}

    provider_return = PROVIDERS[provider](app).register(doc)
    if provider_return:
        if isinstance(provider_return, Response):
            return provider_return
        resp.update(provider_return)

    g.couch[key] = doc
    return jsonify(resp)


@app.route("/v1/confirm/<string:hashkey>/<string:target>")
def confirm_one(hashkey, target):
    try:
        doc = g.couch[hashkey]
        return jsonify({"confirmed": doc["status"] == "confirmed" and
                        doc["target"] == target.strip()})
    except KeyError:
        return jsonify({"confirmed": False})


@app.route("/v1/confirm/", methods=["get", "post"])
def confirm_many():
    if request.method == "POST":
        data = json.loads(request.data)
        target = data["target"].strip()
        to_confirm = data["hashes"]
    else:
        target = request.args.get("target", "").strip()
        to_confirm = request.args.getlist("hashes")

    if not to_confirm or not target:
        return jsonify({"confirmed": False})

    if len(to_confirm) > 100:
        abort(400)

    for hashkey in to_confirm:
        try:
            doc = g.couch[hashkey]
            if doc["status"] != "confirmed" or \
                    doc["target"] != target:
                break
        except KeyError:
            break
    else:
        # We could run through without a break, means we are good
        return jsonify({"confirmed": True})

    return jsonify({"confirmed": False})


@app.route("/v1/contact/", methods=["post"])
def contact():
    try:
        data = json.loads(request.data)
    except (TypeError, ValueError):
        return json_error(400, 'json_decode_error', "Can't decode json.")

    return json_error(400, "execution_failed", "")




@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.config.from_object("itseme.config.DebugConfig")
    celery.config.update(app.config)
    mail.init_app(app)
    app.run()
