# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, g, Response, request, abort, make_response

from itseme.providers import PROVIDERS
from itseme.util import json_error, json_exception, _make_key
from itseme.tasks import celery, mail, contact_request

from couchdb.http import ResourceNotFound

import couchdb
import redis
import json


app = Flask(__name__)


def _get_db():
    return app.couch[app.config["COUCHDB_DATABASE"]]


@app.before_request
def throttle_request():
    if app.config["TESTING"]:
        return
    ip = request.remote_addr
    if int(app.redis.get(ip) or 0) > app.config["REQUEST_THROTTLE"]:
        return json_error(403, "request_limit_reached",
                          "You've reached your requests limit.")
    app.redis.pipeline(
        ).incr(ip
        ).expire(ip, app.config["REQUEST_THROTTLE_SECONDS"]
        ).execute()


@app.before_first_request
def setup_couch():
    if app.config["TESTING"]:
        return
    app.couch = couchdb.Server(app.config["COUCHDB_SERVER"])
    if app.config["COUCHDB_DATABASE"] not in app.couch:
        app.couch.create(app.config["COUCHDB_DATABASE"])

    app.redis = redis.from_url(app.config["REDIS_APP_CACHE"])


@app.before_request
def connect_db():
    g.couch = _get_db()


@app.route("/v1/verify/<string:hashkey>")
def verify(hashkey):
    try:
        PENDING_KEY = "PENDING_%s" % hashkey
        doc = g.couch[PENDING_KEY]
        if doc["status"] != "pending":
            return json_error(403, "not_pending", "Hash isn't pending",
                              {"confirmed": False})
    except (KeyError, ResourceNotFound):
        return json_error(404, "not_found", "Can't find Hash",
                          {"confirmed": False})

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

    # remove it from the old position
    del g.couch[PENDING_KEY]
    # and overwrite an existing one
    g.couch[hashkey] = doc

    return jsonify(resp)


def _is_confirmed(target, prefix=None):
    prefix = prefix or "xmpp"
    return _is_confirmed_hash(_make_key(prefix, target))


def _is_confirmed_hash(hashkey):
    try:
        return g.couch[hashkey]["status"] == "confirmed"
    except (KeyError, ResourceNotFound):
        return False


@app.route("/v1/register/<string:provider>/<string:provider_id>/<string:target>")
def register(provider, provider_id, target):
    target = target.strip()
    if provider != "xmpp" or provider_id != target:
        # let's prove the user is allowed to connect
        if not _is_confirmed(target):
            return json_error(401, "target_unconfirmed",
                              "Please confirm '{}' first.".format(target))

    key = _make_key(provider, provider_id)
    resp = {"status": "pending", "hash": key}

    try:
        doc = g.couch["PENDING_%s" % key]
    except ResourceNotFound:
        doc = {"_id": key, "provider": provider, "target": target,
               "provider_id": provider_id, "status": "pending"}
    else:
        print doc, target
        if doc["target"] == target:
            if not request.args.get("resend"):
                return jsonify(resp)
            else:
                doc["retries"] = doc.get("retries", 0) + 1
        else:
            doc["target"] = target

    provider_return = PROVIDERS[provider](app).register(doc)
    if provider_return:
        if isinstance(provider_return, Response):
            return provider_return
        resp.update(provider_return)

    g.couch["PENDING_%s" % key] = doc
    return jsonify(resp)


@app.route("/v1/confirm/<string:hashkey>/<string:target>")
def confirm_one(hashkey, target):
    try:
        doc = g.couch[hashkey]
        return jsonify({"confirmed": doc["status"] == "confirmed" and
                        doc["target"] == target.strip()})
    except (KeyError, ResourceNotFound):
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
        except (KeyError, ResourceNotFound):
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

    try:
        target = data["target"].strip()

        if not target:
            raise ValueError("Target can't be empty")
        contact_info = data["contact_info"]

        if not contact_info:
            raise ValueError("contact_info can't be empty")
        contacts = data["contacts"]

        if not contacts:
            raise ValueError("contacts can't be empty")
        if len(contacts) > 100:
            raise ValueError("You shall not try to contact more than 100 ppl at once.")
    except (KeyError, ValueError), e:
        return json_exception(e, 400)

    if not _is_confirmed(target):
        return json_error(400, "target_unconfirmed",
                          "Please confirm '{}' first.".format(target))

    confirmed_info = []
    for info in contact_info:
        try:
            protocol = info["protocol"]
            provider_id = info["id"]
            doc = g.couch[_make_key(protocol, provider_id)]
            if doc["status"] == "confirmed" and doc["target"] == target:
                confirmed_info.append(dict(confirmed=True,
                                           protocol=protocol,
                                           id=provider_id
                                           ))
        except (KeyError, TypeError, ValueError, ResourceNotFound):
            pass

    if not confirmed_info:
        return json_error(400, "insufficient_contact_info",
                          "Couldn't confirm any of the given contact info.")

    contact_targets = []
    for hashkey in contacts:
        try:
            doc = g.couch[hashkey]
            if doc["status"] == "confirmed" and doc["target"] != target:
                contact_targets.append(doc["target"])
        except (KeyError, ResourceNotFound):
            pass

    if contact_targets:
        contact_request.delay(list(set(contact_targets)), target, confirmed_info)

    # even if no target found, we do not throw any info
    # to not give away whether we have them or they are
    # confirmed or not. A proper request to /contacts
    # is a shot in the dark and hope for the best for
    # whoever is requesting

    return jsonify({"status": "requests_send"})


@app.route('/')
def hello_world():
    return 'Hello World!'
