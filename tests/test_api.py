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

    def test_login_bad_credentials(self):
        pass

    def test_login_with_existing_token(self):
        pass

    def test_login(self):
        pass

    def test_invalid_token(self):
        pass

    def test_get_user(self):
        pass

    def test_get_current_week_new(self):
        pass

    def test_get_current_week_existing(self):
        pass

    def test_get_week_invalid(self):
        pass

    def test_get_week_new(self):
        pass

    def test_get_week_existing(self):
        pass

    def test_update_current_week_new(self):
        pass

    def test_update_current_week_existing(self):
        pass

    def test_update_week_invalid(self):
        pass

    def test_update_week_new(self):
        pass

    def test_update_week_existing(self):
        pass

    def test_get_weeks_empty(self):
        pass

    def test_get_weeks_all(self):
        pass

    def test_get_weeks_tag_filter(self):
        pass

    def test_get_weeks_pagination(self):
        pass
