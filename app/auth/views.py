from flask import render_template, request, redirect
from flask.helpers import flash, url_for
from flask_login import login_user
from flask_login.utils import login_required, logout_user

from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("main.index"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("auth/login.html.j2", form=form)

    user = User.query.filter_by(email=form.email.data).first()
    if user is None or not user.verify_password(form.password.data):
        flash("Invalid username or password")
        return render_template("auth/login.html.j2", form=form)

    login_user(user, form.remember_me.data)
    next = request.args.get("next")
    if next is None or not next.startswith("/"):
        next = url_for("main.index")
    return redirect(next)
