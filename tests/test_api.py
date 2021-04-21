import unittest

from app import create_app, db


class APITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_foo(self):
        self.assertTrue(False)

    # TODO: login
    # TODO: user
    # TODO: get current week
    # TODO: get specific week
    # TODO: get all weeks
    # TODO: update current week
    # TODO: update specific week