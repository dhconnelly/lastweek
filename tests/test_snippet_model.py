from core.date_utils import iso_week_begin
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
            Snippet(text="bar", year=2012, week=9, tags=[]),
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
            {snippet.text for snippet in self.snippets},
            {snippet.text for snippet in found},
        )

    def test_get_all_no_such_tag(self):
        tag = self.tag.text + "_foo"
        found = Snippet.get_all(user_id=self.user.id, tag_text=tag).all()
        self.assertListEqual([], found)

    def test_get_all_tag(self):
        tag = self.tag.text
        found = Snippet.get_all(user_id=self.user.id, tag_text=tag).all()
        self.assertSetEqual(
            {self.snippets[0].text},
            {snippet.text for snippet in found},
        )

    def test_update_no_such_user(self):
        user_id = self.user.id + 1
        snippet = self.snippets[1]
        self.assertFalse("blargh" in [tag.text for tag in snippet.tags])
        self.assertFalse("blue" in [tag.text for tag in snippet.tags])
        Snippet.update(user_id, snippet.year, snippet.week, "blargh", ["blue"])
        self.assertFalse("blargh" in [tag.text for tag in snippet.tags])
        self.assertFalse("blue" in [tag.text for tag in snippet.tags])

    def test_update_week(self):
        user_id = self.user.id
        snippet = self.snippets[1]
        self.assertNotEqual("blargh", snippet.text)
        self.assertFalse("blue" in {tag.text for tag in snippet.tags})
        Snippet.update(user_id, snippet.year, snippet.week, "blargh", ["blue"])
        after = Snippet.query.get(snippet.id)
        self.assertEqual("blargh", snippet.text)
        self.assertTrue("blue" in {tag.text for tag in after.tags})

    def test_update_week_create_new(self):
        date = iso_week_begin(datetime.date(44, 3, 15))
        (yr, wk, _) = date.isocalendar()
        self.assertIsNone(Snippet.query.filter_by(year=yr, week=wk).first())
        Snippet.update(self.user.id, yr, wk, "beware", ["senate", "prophecy"])
        found = Snippet.query.filter_by(year=yr, week=wk).first()
        self.assertIsNotNone(found)
        self.assertEqual("beware", found.text)
        self.assertSetEqual(
            {"senate", "prophecy"}, {tag.text for tag in found.tags}
        )

    def test_to_json(self):
        snippet = self.snippets[0]
        json = snippet.to_json()
        self.assertEqual(snippet.year, json["year"])
        self.assertEqual(snippet.week, json["week"])
        self.assertEqual(snippet.text, json["text"])
        self.assertSetEqual(
            {tag.text for tag in snippet.tags}, set(json["tags"])
        )

    def test_from_json_new(self):
        date = iso_week_begin(datetime.date(44, 3, 15))
        (yr, wk, _) = date.isocalendar()
        json = {
            "year": yr,
            "week": wk,
            "text": "beware",
            "tags": ["senate", "prophecy"],
        }
        deserialized = Snippet.load_from_json(self.user.id, json)
        self.assertEqual("beware", deserialized.text)
        self.assertEqual(yr, deserialized.year)
        self.assertEqual(wk, deserialized.week)
        self.assertSetEqual(
            {"senate", "prophecy"},
            {tag.text for tag in deserialized.tags},
        )

    def test_from_json_existing(self):
        snippet = self.snippets[1]
        self.assertNotIn("the end", snippet.text)
        self.assertNotIn(self.tag.text, {tag.text for tag in snippet.tags})
        json = {
            "year": snippet.year,
            "week": snippet.week,
            "text": snippet.text + ", the end",
            "tags": [self.tag.text],
        }
        deserialized = Snippet.load_from_json(self.user.id, json)
        self.assertIn("the end", snippet.text)
        self.assertIn(self.tag.text, {tag.text for tag in snippet.tags})
