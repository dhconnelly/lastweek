from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html.j2"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html.j2"), 500


@app.route("/")
def index():
    return render_template("index.html.j2", current_time=datetime.utcnow())


@app.route("/user/<name>")
def user(name):
    langs = list(request.accept_languages)
    return render_template("user.html.j2", name=name, langs=langs)
