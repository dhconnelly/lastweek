from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import HiddenField, TextAreaField, TextField


class SnippetsForm(FlaskForm):
    text = TextAreaField("What have you done this week?")
    year = HiddenField()
    week = HiddenField()
    tags = TextField("Comma-separated tags")
    submit = SubmitField("Save")
