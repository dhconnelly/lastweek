from datetime import date
from typing import NamedTuple, Text, Union

from flask import render_template, redirect, url_for, request, current_app
from werkzeug.wrappers import Response
from flask_login import login_required, current_user
import markdown

from app.main import main
from app.models import Snippet, User
from app import db
from app.main.forms import SnippetsForm


class RenderedSnippet(NamedTuple):
    email: str
    id: int
    week_begin: date
    year: int
    week: int
    content: str
    tags: list


def render_snippet(md: markdown.Markdown, snippet: Snippet) -> RenderedSnippet:
    return RenderedSnippet(
        email=snippet.user.email,
        id=snippet.user.id,
        year=snippet.year,
        week=snippet.week,
        week_begin=date.fromisocalendar(snippet.year, snippet.week, 1),
        content=snippet and md.convert(snippet.text),
        tags=snippet.tags,
    )


def render_snippet_form(
    form: SnippetsForm, user: User, year: int, week: int
) -> Text:
    snippet = lookup_snippet(user, year, week)
    text = snippet and snippet.text
    form.text.data = text
    form.year.data = year
    form.week.data = week
    return render_template(
        "edit.html.j2",
        name=user.name,
        user_id=user.id,
        week_begin=date.fromisocalendar(year, week, 1),
        content=text and markdown.markdown(text),
        form=form,
        tags=snippet and snippet.tags,
    )


def lookup_snippet(user: User, year: int, week: int) -> Snippet:
    snippet = Snippet.query.filter_by(user_id=user.id, year=year, week=week)
    return snippet.first()


def update_snippet(user: User, year: int, week: int, text: str):
    snippet = lookup_snippet(user, year, week)
    if not snippet:
        snippet = Snippet(user_id=user.id, year=year, week=week)
    snippet.text = text
    db.session.add(snippet)
    db.session.commit()


@main.route("/", methods=["GET", "POST"])
def index() -> Union[Response, Text]:
    if current_user.is_authenticated:
        return redirect("/edit")
    return render_template("index.html.j2")


@main.route("/edit", methods=["GET", "POST"])
@main.route("/edit/<int:year>/<int:week>", methods=["GET", "POST"])
@login_required
def edit(year=None, week=None) -> Union[Response, Text]:
    if not year or not week:
        (year, week, _) = date.today().isocalendar()
        return redirect(url_for(".edit", year=year, week=week))
    # if updating, always redirect to the same week
    form = SnippetsForm()
    if form.validate_on_submit():
        update_snippet(current_user, year, week, form.text.data)
        return redirect(url_for(".edit", year=year, week=week))
    return render_snippet_form(form, current_user, year, week)


@main.route("/history", methods=["GET", "POST"])
@login_required
def history() -> Union[Response, Text]:
    page = request.args.get("page", 1, type=int)
    md = markdown.Markdown()
    snippets = Snippet.query.filter_by(user_id=current_user.id)
    snippets = snippets.order_by(Snippet.year.desc(), Snippet.week.desc())
    pagination = snippets.paginate(
        page,
        per_page=current_app.config["LASTWEEK_SNIPPETS_PER_PAGE"],
        error_out=True,
    )
    snippets = [render_snippet(md, s) for s in pagination.items]
    return render_template(
        "history.html.j2", snippets=snippets, pagination=pagination
    )
