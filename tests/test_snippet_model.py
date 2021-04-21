from app import create_app, db
import unittest


class SnippetModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_foo(self):
        self.assertTrue(False)


# TODO: get_all
# TODO: get_by_week
# TODO: update
# TODO: get/from_json