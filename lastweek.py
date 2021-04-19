import os

from flask_migrate import Migrate

from app import create_app, db
from app.models import User, Snippet, Tag, tagged_snippets

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Snippet=Snippet,
        Tag=Tag,
        tagged_snippets=tagged_snippets,
    )


@app.cli.command()
def fill_db():
    """Fills the dev database with fake data."""
    if not app.config.get("DEV"):
        return
    from fill_db import fill_db

    fill_db(db)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)