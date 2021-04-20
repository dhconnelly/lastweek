from app.api.errors import unauthorized
from flask.globals import g
from app.models import Snippet, User
from flask.json import jsonify
from . import api


@api.route("/users/<int:user_id>")
def get_user(user_id):
    if user_id != g.current_user.id:
        return unauthorized()
    return jsonify(g.current_user.to_json())


@api.route("/users/<int:user_id>/weeks/")
def get_user_weeks(user_id):
    if user_id != g.current_user.id:
        return unauthorized()
    weeks = g.current_user.snippets
    return jsonify([week.to_json() for week in weeks])


@api.route("/users/<int:user_id>/weeks/<int:year>/<int:week>")
def get_user_week(user_id, year, week):
    if user_id != g.current_user.id:
        return unauthorized()
    # TODO: validate the week and year
    week = Snippet.query.filter_by(year=year, week=week).first()
    if week is None:
        # don't worry about actually adding to the database until user saves
        week = Snippet(user_id=g.current_user.id, year=year, week=week)
    return jsonify(week.to_json())
