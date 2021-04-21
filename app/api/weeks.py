from flask.helpers import url_for
from app.api.errors import ValidationError
from flask import jsonify
from flask.globals import current_app, g, request

from . import api
from app.models import Snippet, get_snippets, lookup_snippet, update_snippet
from core.date_utils import is_valid_iso_week, this_week


@api.route("/weeks/")
def get_weeks():
    page = request.args.get("page", 1, type=int)
    snippets = get_snippets(g.current_user, tag_text=request.args.get("tag"))
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
def get_week(year=None, week=None):
    if not year or not week:
        (year, week) = this_week()
    if not is_valid_iso_week(year, week):
        raise ValidationError("invalid ISO week date")
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
    if not is_valid_iso_week(year, week):
        raise ValidationError("invalid ISO week date")
    text = request.json.get("text", "")
    tags = request.json.get("tags", [])
    update_snippet(g.current_user, year, week, text, tags)
    return jsonify({"success": True})