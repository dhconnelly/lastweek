from datetime import date
from app.email import send_email
from flask import render_template, request, redirect
from flask.helpers import flash, url_for
from flask_login import login_user, current_user
from flask_login.utils import login_required, logout_user

from app import db
from app.auth import auth
from app.models import User
from app.auth.forms import (
    ChangePasswordForm,
    LoginForm,
    RegistrationForm,
    RequestResetPasswordForm,
    ResetPasswordForm,
)


@auth.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and request.blueprint != "auth"
        and request.endpoint != "static"
    ):
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html.j2")


def send_token(user, token, message, template):
    send_email(
        user.email,
        message,
        template,
        user=user,
        token=token,
    )


@auth.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ChangePasswordForm()
    if not form.validate_on_submit():
        return render_template("auth/settings.html.j2", form=form)
    if not current_user.verify_password(form.old_password.data):
        flash("Incorrect current password")
        return render_template("auth/settings.html.j2", form=form)
    current_user.password = form.new_password.data
    db.session.add(current_user)
    db.session.commit()
    flash("Your password has been updated")
    return redirect(url_for("auth.settings"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_token(
        current_user, token, "Confirm your account", "auth/email/confirm"
    )
    flash("A new confirmation link has been sent via email")
    return redirect(url_for("main.index"))


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/request_reset", methods=["GET", "POST"])
def request_reset():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = RequestResetPasswordForm()
    if not form.validate_on_submit():
        return render_template("auth/request_reset.html.j2", form=form)
    email = form.email.data.lower()
    user = User.query.filter_by(email=email).first()
    if user:
        token = user.generate_reset_token()
        send_token(user, token, "Reset your password", "auth/email/reset")
    flash("If a matching account was found, a reset email has been sent.")
    return redirect(url_for("auth.login"))


@auth.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if not form.validate_on_submit():
        return render_template("auth/reset.html.j2", form=form)
    if User.reset_password(token, form.new_password.data):
        flash("Your password has been updated")
    else:
        flash("Password reset failed. Please try again")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template("auth/register.html.j2", form=form)
    user = User(
        name=form.name.data,
        email=form.email.data,
        password=form.password.data,
        member_since=date.today(),
    )
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    send_token(user, token, "Confirm your account", "auth/email/confirm")
    flash("A confirmation link has been sent to you via email")
    return redirect(url_for("auth.login"))


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
