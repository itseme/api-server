from flask import make_response, jsonify

import hashlib
import random
import re

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def convert(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

def json_error(code, name, message, custom_json=None):
    json = custom_json or {}
    json["error"] = dict(code=name, message=message)
    return make_response( (jsonify(json), code, {}) )


def json_exception(exc, code=500):
    return json_error(code, convert(exc.__class__.__name__), "{}".format(exc))

def _make_key(*args):
    return hashlib.sha512(":".join(args)).hexdigest()

def _generate_code(length=4):
    return "{0:.10}".format(random.random())[2:2 + length]
