from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    Email,
    ValidationError,
)


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 255)])
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 320), Email()]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match!"),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered")


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 320), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")
