from datetime import date
from typing import NamedTuple, Text

from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask.wrappers import Response
import markdown

from app.main import main
from app.models import Snippet, User
from app import db
from app.main.forms import SnippetsForm


def iso_week_begin(d: date) -> date:
    iso = d.isocalendar()
    return date.fromisocalendar(iso[0], iso[1], 1)


class RenderedSnippet(NamedTuple):
    email: str
    id: int
    week_begin: date
    content: str


def render_snippet(md: markdown.Markdown, snippet: Snippet) -> RenderedSnippet:
    return RenderedSnippet(
        email=snippet.user.email,
        id=snippet.user.id,
        week_begin=snippet.week_begin,
        content=snippet and md.convert(snippet.text),
    )


def render_snippet_form(
    form: SnippetsForm, user: User, week_begin: date
) -> Text:
    snippet = lookup_snippet(user, week_begin)
    text = snippet and snippet.text
    form.text.data = text
    form.week_begin.data = week_begin
    return render_template(
        "edit.html.j2",
        name=user.name,
        user_id=user.id,
        week_begin=week_begin,
        content=text and markdown.markdown(text),
        form=form,
    )


def lookup_snippet(user: User, week_begin: date) -> Snippet:
    snippet = Snippet.query.filter_by(user_id=user.id, week_begin=week_begin)
    return snippet.first()


def update_snippet(user: User, week_begin: date, text: str):
    snippet = lookup_snippet(user, week_begin)
    if not snippet:
        snippet = Snippet(user_id=user.id, week_begin=week_begin)
    snippet.text = text
    db.session.add(snippet)
    db.session.commit()


@main.route("/", methods=["GET", "POST"])
def index() -> Response:
    if current_user.is_authenticated:
        return redirect("/edit")
    return render_template("index.html.j2")


@main.route("/edit", methods=["GET", "POST"])
@main.route("/edit/<int:y>/<int:m>/<int:d>", methods=["GET", "POST"])
@login_required
def edit(y=None, m=None, d=None) -> Response:
    # redirect to the first day of the week if necessary
    requested_date = y and m and d and date(y, m, d)
    week_begin = iso_week_begin(requested_date or date.today())
    if requested_date != week_begin:
        (y, m, d) = (week_begin.year, week_begin.month, week_begin.day)
        return redirect(url_for(".edit", y=y, m=m, d=d))

    # if updating, always redirect to the same week
    form = SnippetsForm()
    if form.validate_on_submit():
        update_snippet(current_user, week_begin, form.text.data)
        return redirect(url_for(".edit", y=y, m=m, d=d))

    return render_snippet_form(form, current_user, week_begin)


@main.route("/history", methods=["GET", "POST"])
@login_required
def history() -> Response:
    user_snippets = Snippet.query.filter_by(user_id=current_user.id)
    ordered_snippets = user_snippets.order_by(Snippet.week_begin.desc())
    md = markdown.Markdown()
    rendered = [render_snippet(md, s) for s in ordered_snippets]
    return render_template("history.html.j2", snippets=rendered)
