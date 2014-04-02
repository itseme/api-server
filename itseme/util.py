from flask import make_response, jsonify

import hashlib
import random

def json_error(code, name, message, custom_json=None):
    json = custom_json or {}
    json["error"] = dict(code=name, message=message)
    return make_response( (jsonify(json), code, {}) )


def json_exception(exc, code=500):
    return json_error(code, exc.__class__.__name__, "{}".format(exc))

def _make_key(*args):
    return hashlib.sha512(":".join(args)).hexdigest()

def _generate_code(length=4):
    return "{0:.10}".format(random.random())[2:2 + length]
