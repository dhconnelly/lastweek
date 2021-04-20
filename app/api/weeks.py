from flask import jsonify
from flask.globals import g

from . import api
from app.models import Snippet
from core.date_utils import this_week


@api.route("/weeks/")
def get_weeks():
    weeks = g.current_user.snippets.order_by(
        Snippet.year.desc(), Snippet.week.desc()
    )
    return jsonify([week.to_json() for week in weeks])


@api.route("/weeks/current")
@api.route("/weeks/<int:year>/<int:week>")
def get_week(year=None, week=None):
    if year is None:
        (year, week) = this_week()
    # TODO: validate the week and year
    snippet = Snippet.query.filter_by(
        user_id=g.current_user.id, year=year, week=week
    ).first()
    if snippet is None:
        # don't worry about actually adding to the database until user saves
        snippet = Snippet(user_id=g.current_user.id, year=year, week=week)
    return jsonify(snippet.to_json())
