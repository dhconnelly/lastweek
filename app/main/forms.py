from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import HiddenField, TextAreaField


class SnippetsForm(FlaskForm):
    text = TextAreaField("What have you done this week?")
    week_begin = HiddenField()
    submit = SubmitField("Save")
