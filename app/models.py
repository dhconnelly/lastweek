from flask.globals import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index

from app import db
from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(320), unique=True, index=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    member_since = db.Column(db.Date, nullable=False)

    snippets = db.relationship("Snippet", backref="user", lazy="dynamic")

    def generate_confirmation_token(self, expiration=3600):
        s = TimedSerializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})

    def confirm(self, token):
        s = TimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        print(token, data)
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {repr(self.email)}>"


class Snippet(db.Model):
    __tablename__ = "snippets"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.UnicodeText, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.Index("iso_week_date", "year", "week"),)

    def __repr__(self):
        return f"<Snippet {repr(self.user.email)} {self.year} {self.week}>"
