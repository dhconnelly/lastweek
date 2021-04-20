from flask.globals import g
from flask.json import jsonify

from . import api


@api.route("/user")
def get_user():
    return jsonify(g.current_user.to_json())
