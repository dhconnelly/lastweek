from __future__ import annotations

from typing import List, Optional
from flask.globals import current_app
from flask.helpers import url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from sqlalchemy.orm.query import Query
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login_manager
from core.date_utils import iso_week_begin, this_week


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

    def to_json(self):
        (year, week) = this_week()
        json = {
            "name": self.name,
            "email": self.email,
            "member_since": self.member_since.isoformat(),
        }
        return json

    def generate_auth_token(self, expiration):
        s = TimedSerializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"id": self.id}).decode("utf-8")

    def generate_confirmation_token(self, expiration=3600):
        s = TimedSerializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    def generate_reset_token(self, expiration=3600):
        s = TimedSerializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id}).decode("utf-8")

    @staticmethod
    def verify_auth_token(token):
        s = TimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data["id"])

    @staticmethod
    def reset_password(token, password):
        s = TimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if (user_id := data.get("reset")) is None:
            return False
        if (user := User.query.get(int(user_id))) is None:
            return False
        user.password = password
        db.session.add(user)
        db.session.commit()
        return True

    def confirm(self, token):
        s = TimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
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
        return f"<User {self.id} {repr(self.email)}>"


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.UnicodeText, nullable=False)

    @staticmethod
    def get_all(texts: List[str]) -> List[Tag]:
        tags = []
        for text in set(texts):
            tag = Tag.query.filter_by(text=text).first()
            if not tag:
                tag = Tag(text=text)
                db.session.add(tag)
            tags.append(tag)
        return tags

    def __repr__(self):
        return f"<Tag {self.id} {self.text}>"


tagged_snippets = db.Table(
    "tagged_snippets",
    db.Column("snippet_id", db.Integer, db.ForeignKey("snippets.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
)


class Snippet(db.Model):
    __tablename__ = "snippets"
    __table_args__ = (db.Index("iso_week_date", "year", "week"),)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.UnicodeText, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    tags = db.relationship(
        "Tag",
        secondary=tagged_snippets,
        backref=db.backref("snippets", lazy="dynamic"),
        lazy="dynamic",
    )

    @staticmethod
    def load_from_json(user_id, json):
        """Loads a snippet from a dictionary.

        If an existing snippet with this date is found, that one is updated,
        committed to the database, and returned. Otherwise a new instance is
        populated, committed to the database, and returned.
        """
        year = json["year"]
        week = json["week"]
        text = json.get("text", "")
        tags = json.get("tags", [])
        return Snippet.update(user_id, year, week, text, tags)

    def to_json(self):
        """Serializes this snippet to a dictionary."""
        json = {
            "url": url_for(
                "api.get_week",
                year=self.year,
                week=self.week,
            ),
            "year": self.year,
            "week": self.week,
            "text": self.text or "",
            "tags": [tag.text for tag in self.tags],
        }
        return json

    @staticmethod
    def get_by_week(user_id: str, year: int, week: int) -> Optional[Snippet]:
        """Returns the specified snippet (or None if it does not exist)."""
        snippet = Snippet.query.filter_by(
            user_id=user_id, year=year, week=week
        )
        return snippet.first()

    @staticmethod
    def update(user_id: str, year: int, week: int, text: str, tags: List[str]):
        snippet = Snippet.get_by_week(user_id, year, week)
        if not snippet:
            snippet = Snippet(user_id=user_id, year=year, week=week)
        snippet.text = text
        snippet.tags = Tag.get_all(tags)
        db.session.add(snippet)
        db.session.commit()
        return snippet

    @staticmethod
    def get_all(user_id, tag_text=None) -> Query:
        """Returns a query for all the specified snippets."""
        query = Snippet.query.filter_by(user_id=user_id)
        if tag_text:
            tag = Tag.query.filter_by(text=tag_text).first()
            tag_id = tag and tag.id
            query = query.join(tagged_snippets).filter_by(tag_id=tag_id)
        return query.order_by(Snippet.year.desc(), Snippet.week.desc())

    def __repr__(self):
        return f"<Snippet {self.id} {self.user.email} {self.text} {self.year} {self.week}>"
