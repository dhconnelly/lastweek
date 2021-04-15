from time import sleep
import unittest

from app import create_app, db
from app.models import User


class UserModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password="cat")
        self.assertIsNotNone(u.password_hash)

    def test_get_password_getter(self):
        u = User(password="cat")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password="cat")
        self.assertFalse(u.verify_password("dog"))
        self.assertTrue(u.verify_password("cat"))

    def test_password_salts_are_random(self):
        u1 = User(password="cat")
        u2 = User(password="cat")
        self.assertNotEqual(u1.password_hash, u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(
            name="bob",
            email="bob@example.com",
            password="cat",
            confirmed=False,
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(
            name="bob",
            email="bob@example.com",
            password="cat",
            confirmed=False,
        )
        u2 = User(
            name="fred",
            email="fred@example.com",
            password="cat",
            confirmed=False,
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(
            name="bob",
            email="bob@example.com",
            password="cat",
            confirmed=False,
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(0)
        sleep(1)  # TODO: seems bad
        self.assertFalse(u.confirm(token))
