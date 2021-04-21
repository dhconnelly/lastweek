from flask.helpers import url_for
from app.api.errors import ValidationError, unauthorized
from flask import jsonify
from flask.globals import current_app, g, request

from . import api
from .decorators import validate_week
from app.models import Snippet
from core.date_utils import is_valid_iso_week, this_week


@api.route("/login", methods=["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid credentials")
    token = g.current_user.generate_auth_token(expiration=3600)
    return jsonify({"token": token, "expiration": 3600})


@api.route("/user")
def get_user():
    return jsonify(g.current_user.to_json())


@api.route("/weeks/")
def get_weeks():
    page = request.args.get("page", 1, type=int)
    tag = request.args.get("tag")
    snippets = Snippet.get_all(g.current_user.id, tag_text=tag)

    pagination = snippets.paginate(
        page,
        per_page=current_app.config["LASTWEEK_SNIPPETS_PER_PAGE"],
        error_out=True,
    )
    snippets = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for("api.get_weeks", page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for("api.get_weeks", page=page + 1)

    return jsonify(
        {
            "weeks": [snippet.to_json() for snippet in snippets],
            "prev_url": prev,
            "next_url": next,
            "count": pagination.total,
        }
    )


@api.route("/weeks/current")
@api.route("/weeks/<int:year>/<int:week>")
@validate_week
def get_week(year=None, week=None):
    if not year or not week:
        (year, week) = this_week()
    snippet = Snippet.get_by_week(g.current_user.id, year, week)
    if snippet is None:
        # don't worry about actually adding to the database until user saves
        snippet = Snippet(user_id=g.current_user.id, year=year, week=week)
    return jsonify(snippet.to_json())


@api.route("/weeks/current", methods=["PUT", "POST"])
@api.route("/weeks/<int:year>/<int:week>", methods=["PUT", "POST"])
@validate_week
def update_week(year=None, week=None):
    if not year or not week:
        (year, week) = this_week()
    text = request.json.get("text", "")
    tags = request.json.get("tags", [])
    Snippet.update(g.current_user, year, week, text, tags)
    return jsonify({"success": True})