from datetime import datetime
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
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# TODO: move this to env var
app.config["SECRET_KEY"] = "der geist der stets verneint"

bootstrap = Bootstrap(app)
moment = Moment(app)


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
