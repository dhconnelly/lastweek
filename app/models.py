from app import db


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
