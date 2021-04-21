import unittest

from app import create_app, db
from app.models import Tag


class TagModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_creates_new_tags(self):
        self.assertIsNone(Tag.query.filter_by(text="foo").first())
        self.assertIsNone(Tag.query.filter_by(text="bar").first())
        tags = Tag.get_all(["foo", "bar"])
        self.assertIsNotNone(Tag.query.filter_by(text="foo").first())
        self.assertIsNotNone(Tag.query.filter_by(text="bar").first())

    def test_get_all_reuses_existing_tags(self):
        tag = Tag(text="foo")
        db.session.add(tag)
        db.session.commit()
        self.assertEqual(1, Tag.query.filter_by(text="foo").count())

        tags = Tag.get_all(["foo"])
        self.assertEqual(1, Tag.query.filter_by(text="foo").count())
        self.assertEqual(tag.id, tags[0].id)

    def test_get_all_eliminates_duplicates(self):
        tags = Tag.get_all(["foo", "foo"])
        self.assertEqual(1, len(tags))
        self.assertEqual(1, Tag.query.filter_by(text="foo").count())