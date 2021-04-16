from datetime import date
from app.models import User
import unittest

from app.auth.forms import RegistrationForm
from app import create_app, db


def valid_form():
    form = RegistrationForm()
    form.name.data = "bob"
    form.email.data = "bob@example.com"
    form.password.data = "abc"
    form.password2.data = "abc"
    return form


class RegistrationFormTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_validate(self):
        with self.app.test_request_context("/"):
            form = valid_form()
        self.assertTrue(form.validate())

    def test_required_fields(self):
        with self.app.test_request_context("/"):
            form = valid_form()
        for field in ("name", "email", "password", "password2"):
            prev = form[field].data
            form[field].data = None
            self.assertFalse(form.validate())
            form[field].data = prev

    def test_passwords_match(self):
        with self.app.test_request_context("/"):
            form = valid_form()
        form.password2.data = form.password2.data + "abc"
        self.assertFalse(form.validate())

    def test_email_unique(self):
        with self.app.test_request_context("/"):
            form = valid_form()
        db.session.add(
            User(
                name="fred",
                email=form.email.data,
                password_hash="abc",
                confirmed=False,
                member_since=date.today(),
            )
        )
        db.session.commit()
        self.assertFalse(form.validate())
        form.email.data = "abc" + form.email.data
        self.assertTrue(form.validate())
