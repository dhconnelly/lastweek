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
from wtforms.validators import DataRequired

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


class SnippetsForm(FlaskForm):
    snippet = StringField("What did you do?", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html.j2"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html.j2"), 500


def render(name):
    form = SnippetsForm()
    if form.validate_on_submit():
        old_snippet = session.get("snippet")
        if old_snippet is not None and old_snippet != form.snippet.data:
            flash("Updated snippet")
        session["snippet"] = form.snippet.data
        return redirect(url_for("index"))
    return render_template(
        "index.html.j2", name=name, form=form, snippet=session.get("snippet")
    )


@app.route("/", methods=["GET", "POST"])
def index():
    return render("Stranger")


@app.route("/user/<name>", methods=["GET", "POST"])
def user(name):
    return render(name)
