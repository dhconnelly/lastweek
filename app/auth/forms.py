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


class RequestResetPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update password")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("new_password2", message="Passwords must match!"),
        ],
    )
    new_password2 = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update password")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Current password", validators=[DataRequired()]
    )
    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("new_password2", message="Passwords must match!"),
        ],
    )
    new_password2 = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update password")


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
