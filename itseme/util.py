from flask import make_response, jsonify

def json_error(code, name, message, custom_json=None):
    json = custom_json or {}
    json["error"] = dict(code=name, message=message)
    return make_response( (jsonify(json), code, {}) )


def json_exception(exc, code=500):
    json_error(code, exc.__class__.__name__, "{}".format(exc))
