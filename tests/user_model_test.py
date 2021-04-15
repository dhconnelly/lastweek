import unittest
from app.models import User


class UserModelTest(unittest.TestCase):
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