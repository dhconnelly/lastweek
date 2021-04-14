import os
from datetime import date, datetime
from flask import (
    Flask,
    request,
    render_template,
    session,
    redirect,
    url_for,
    flash,
)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, SubmitField
from wtforms.fields.core import SelectField
from wtforms.fields.simple import HiddenField, TextAreaField
from wtforms.validators import DataRequired
import markdown

app = Flask(__name__)

# TODO: move these to env vars
app.config["SECRET_KEY"] = "der geist der stets verneint"
basedir = os.path.abspath(os.path.dirname(__file__))
db_uri = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


def iso_week_begin(d: date) -> date:
    iso = d.isocalendar()
    return date.fromisocalendar(iso[0], iso[1], 1)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(320), unique=True, index=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    snippets = db.relationship("Snippet", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {repr(self.email)}>"


class Snippet(db.Model):
    __tablename__ = "snippets"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.UnicodeText)
    week_begin = db.Column(db.Date, nullable=False, index=True)

    def __repr__(self):
        return f"<Snippet {repr(self.user.email)} {repr(self.week_begin)}>"


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Snippet=Snippet)


class SnippetsForm(FlaskForm):
    text = TextAreaField("What have you done this week?")
    week_begin = HiddenField()
    submit = SubmitField("Save")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html.j2"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html.j2"), 500


def render_snippet(md, snippet):
    return {
        "email": snippet.user.email,
        "id": snippet.user.id,
        "week_begin": snippet.week_begin,
        "content": snippet and md.convert(snippet.text),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    snippets = Snippet.query.order_by(Snippet.week_begin.desc()).all()
    md = markdown.Markdown()
    rendered = [render_snippet(md, s) for s in snippets]
    return render_template("index.html.j2", snippets=rendered)


def render_edit_form(form, user, week_begin, text):
    md = markdown.Markdown()
    form.text.data = text
    form.week_begin.data = week_begin
    return render_template(
        "user.html.j2",
        name=user.name,
        user_id=user.id,
        week_begin=week_begin,
        content=text and md.convert(text),
        form=form,
    )


def lookup_snippet(user, week_begin):
    snippet = Snippet.query.filter_by(user_id=user.id, week_begin=week_begin)
    return snippet.first()


def edit_week(form, week_begin, user):
    snippet = lookup_snippet(user, week_begin)
    return render_edit_form(form, user, week_begin, snippet and snippet.text)


@app.route("/user/<id>/week/<int:y>/<int:m>/<int:d>", methods=["GET", "POST"])
def edit(id, y, m, d):
    user = User.query.get(id)
    if not user:
        return render_template("404.html.j2"), 404

    # redirect to the first day of the week if necessary
    form = SnippetsForm()
    requested_date = date(y, m, d)
    week_begin = iso_week_begin(requested_date)
    if requested_date != week_begin:
        (y, m, d) = (week_begin.year, week_begin.month, week_begin.day)
        return redirect(url_for("edit", id=user.id, y=y, m=m, d=d))

    # if this is just a get, render the editor for this week
    if not form.validate_on_submit():
        return edit_week(form, week_begin, user)

    # overwrite the existing snippet if it exists
    snippet = lookup_snippet(user, week_begin)
    if not snippet:
        snippet = Snippet(user_id=user.id, week_begin=week_begin)
    snippet.text = form.text.data
    db.session.add(snippet)
    db.session.commit()
    return redirect(url_for("edit", id=user.id, y=y, m=m, d=d))


@app.route("/user/<id>", methods=["GET", "POST"])
def user(id):
    user = User.query.get(id)
    if not user:
        return render_template("404.html.j2"), 404
    today = date.today()
    (y, m, d) = (today.year, today.month, today.day)
    return redirect(url_for("edit", id=user.id, y=y, m=m, d=d))


@app.route("/user/<id>/history", methods=["GET", "POST"])
def user_history(id):
    user = User.query.get(id)
    user_snippets = Snippet.query.filter_by(user_id=user.id)
    ordered_snippets = user_snippets.order_by(Snippet.week_begin.desc())
    md = markdown.Markdown()
    rendered = [render_snippet(md, s) for s in ordered_snippets]
    return render_template("user_history.html.j2", snippets=rendered)
