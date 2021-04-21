import datetime
import unittest

from app.models import Snippet, Tag, User
from app import create_app, db


class SnippetModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate(self):
        self.tag = Tag(text="blue")
        self.snippets = [
            Snippet(text="foo", year=2017, week=17, tags=[self.tag]),
            Snippet(text="bar", year=2017, week=17, tags=[]),
        ]
        self.user = User(
            email="julius.caesar@example.com",
            name="Julius Caesar",
            password="rubicon",
            confirmed=True,
            member_since=datetime.date.today(),
            snippets=self.snippets,
        )
        db.session.add(self.user)
        db.session.commit()

    def test_get_by_week_no_such_user(self):
        year = self.snippets[0].year
        week = self.snippets[0].week
        user_id = self.snippets[0].user_id + 1
        self.assertIsNone(Snippet.get_by_week(user_id, year, week))

    def test_get_by_week_missing_year(self):
        year = self.snippets[0].year + 1
        week = self.snippets[0].week
        user_id = self.snippets[0].user_id
        self.assertIsNone(Snippet.get_by_week(user_id, year, week))

    def test_get_by_week_missing_week(self):
        year = self.snippets[0].year
        week = self.snippets[0].week + 1
        user_id = self.snippets[0].user_id
        self.assertIsNone(Snippet.get_by_week(user_id, year, week))

    def test_get_by_week(self):
        year = self.snippets[0].year
        week = self.snippets[0].week
        user_id = self.snippets[0].user_id
        found = Snippet.get_by_week(user_id, year, week)
        self.assertIsNotNone(found)
        self.assertEqual(self.snippets[0].id, found.id)

    def test_get_all_no_such_user(self):
        user_id = self.user.id + 1
        self.assertListEqual([], Snippet.get_all(user_id).all())

    def test_get_all_empty(self):
        user = User(
            name="bob",
            email="bob@example.com",
            confirmed=True,
            member_since=datetime.date.today(),
            password="cat",
        )
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(User.query.get(user.id))
        self.assertListEqual([], Snippet.get_all(user_id=user.id).all())

    def test_get_all(self):
        found = Snippet.get_all(user_id=self.user.id).all()
        self.assertSetEqual(
            set(snippet.text for snippet in self.snippets),
            set(snippet.text for snippet in found),
        )

    def test_get_all_no_such_tag(self):
        tag = self.tag.text + "_foo"
        found = Snippet.get_all(user_id=self.user.id, tag_text=tag).all()
        self.assertListEqual([], found)

    def test_get_all_tag(self):
        tag = self.tag.text
        found = Snippet.get_all(user_id=self.user.id, tag_text=tag).all()
        self.assertSetEqual(
            set([self.snippets[0].text]),
            set(snippet.text for snippet in found),
        )


# TODO: update
# TODO: get/from_json