from app import Snippet, User, iso_week_begin
from datetime import date


def init(db):
    db.create_all()


users = [
    {"email": "bob@example.com", "name": "Bob"},
    {"email": "jürgen.müller@example.com", "name": "Jürgen Müller"},
    {"email": "léa.léa@example.com", "name": "Léa de la Bonne Chance"},
]

snippets = [
    {
        "user_email": "bob@example.com",
        "text": "did nothing :(",
        "date": date(2021, 1, 8),
    },
    {
        "user_email": "bob@example.com",
        "text": "did a lot!",
        "date": date(2020, 4, 13),
    },
    {
        "user_email": "jürgen.müller@example.com",
        "text": """- Heute frühstückten wir draußen
- Dann ging ich in den Wald spazieren
- Abends schauten wir Fernsehen
""",
        "date": date(2020, 7, 4),
    },
    {
        "user_email": "jürgen.müller@example.com",
        "text": "Eine Million Dollar verspielt",
        "date": date(2020, 5, 29),
    },
    {
        "user_email": "jürgen.müller@example.com",
        "text": "den Teufel aufm Berg gesehen",
        "date": date(2019, 1, 1),
    },
    {
        "user_email": "jürgen.müller@example.com",
        "text": "erst kommt das Geld, dann kommt die Moral",
        "date": date(2021, 1, 2),
    },
    {
        "user_email": "jürgen.müller@example.com",
        "text": "struck me like a chord",
        "date": date(2017, 11, 13),
    },
    {
        "user_email": "léa.léa@example.com",
        "text": "n/a",
        "date": date(2021, 1, 7),
    },
    {
        "user_email": "léa.léa@example.com",
        "text": "je ne sais pas",
        "date": date(2020, 12, 31),
    },
    {
        "user_email": "léa.léa@example.com",
        "text": "forsan et haec olim meminisse iuvabit",
        "date": date(2020, 12, 24),
    },
]


def populate_all(db):
    user_rows = {}
    for user in users:
        row = User(**user)
        user_rows[user["email"]] = row
        db.session.add(row)
    for snippet in snippets:
        user = user_rows[snippet["user_email"]]
        date = iso_week_begin(snippet["date"])
        row = Snippet(text=snippet["text"], user=user, week_begin=date)
        db.session.add(row)
    db.session.commit()


def fill(db):
    init(db)
    populate_all(db)
