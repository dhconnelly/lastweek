from flask.json import jsonify
from app.main.errors import forbidden
from flask.globals import g
from flask_httpauth import HTTPBasicAuth
from werkzeug.wrappers import Response

from app.models import User
from app.api.errors import unauthorized
from app.api import api

auth = HTTPBasicAuth()


@auth.error_handler
def auth_error() -> Response:
    return unauthorized("Invalid credentials")


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden("Unconfirmed account")


@api.route("/tokens/", methods=["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid credentials")
    return jsonify(
        {
            "token": g.current_user.generate_auth_token(expiration=3600),
            "expiration": 3600,
        }
    )


@auth.verify_password
def verify_password(email_or_token: str, password: str) -> bool:
    if email_or_token == "":
        return False
    if password == "":
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)