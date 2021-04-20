from flask import jsonify
from flask.globals import g, request

from . import api
from app.models import Snippet, get_snippets, lookup_snippet, update_snippet
from core.date_utils import this_week


@api.route("/weeks/")
def get_weeks():
    tag = request.args.get("tag")
    snippets = get_snippets(g.current_user, tag_text=tag)
    # TODO: paginate
    return jsonify([snippet.to_json() for snippet in snippets])


@api.route("/weeks/current")
@api.route("/weeks/<int:year>/<int:week>")
def get_week(year=None, week=None):
    if not year or not week:
        (year, week) = this_week()
    # TODO: validate the week and year
    snippet = lookup_snippet(g.current_user, year, week)
    if snippet is None:
        # don't worry about actually adding to the database until user saves
        snippet = Snippet(user_id=g.current_user.id, year=year, week=week)
    return jsonify(snippet.to_json())


@api.route("/weeks/current", methods=["PUT", "POST"])
@api.route("/weeks/<int:year>/<int:week>", methods=["PUT", "POST"])
def update_week(year=None, week=None):
    if not year or not week:
        (year, week) = this_week()
    # TODO: validate the week and year
    text = request.json.get("text", "")
    tags = request.json.get("tags", [])
    update_snippet(g.current_user, year, week, text, tags)
    return jsonify({"success": True})