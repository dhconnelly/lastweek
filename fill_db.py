import random
from datetime import date
from mimesis.providers.generic import Generic

from sqlalchemy.exc import IntegrityError

from app.models import Snippet, User
from core.date_utils import iso_week_begin


class LastweekFaker:
    def __init__(self, db, faker):
        self.db = db
        self.faker = faker
        self.users = {}
        self.user_emails = []
        self.user_snippet_dates = {}
        self.snippets = []

    def commit_all(self):
        for user in self.users.values():
            self.db.session.add(user)
        for snippet in self.snippets:
            self.db.session.add(snippet)
        self.db.session.commit()

    def fake_user(self, password):
        """Creates a fake user with the given password."""
        email = self.faker.person.email(unique=True)
        user = User(
            email=email,
            name=self.faker.person.full_name(),
            password=password,
            confirmed=True,
            member_since=date.fromtimestamp(0),
        )
        self.users[email] = user
        self.user_emails.append(email)
        self.user_snippet_dates[email] = set()

    def fake_snippet(self):
        """Creates a fake snippet for a random user from the given set."""
        user_email = random.choice(self.user_emails)
        user = self.users[user_email]
        dates = self.user_snippet_dates[user_email]
        date = None
        while True:
            date = iso_week_begin(self.faker.datetime.date())
            if date not in dates:
                break
        dates.add(date)
        (year, week, _) = date.isocalendar()
        snippet = Snippet(
            user=user,
            text=self.faker.text.text(),
            year=year,
            week=week,
        )
        self.snippets.append(snippet)


def fill_db(db, password="p@ssw0rd", user_count=20, snippet_count=1000):
    print("Filling dev database with fake data...")
    db.create_all()
    faker = LastweekFaker(db, Generic())
    for i in range(user_count):
        faker.fake_user(password)
    print(f"Created {user_count} users.")
    for i in range(snippet_count):
        faker.fake_snippet()
    print(f"Created {snippet_count} snippets.")
    print(f"Committing to database...")
    faker.commit_all()
    print("Done.")
