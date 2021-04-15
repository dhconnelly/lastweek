from flask import render_template, current_app
from flask_mail import Message

from app import mail


def send_email(to, subject, template, **kwargs):
    msg = Message(
        current_app.config["LASTWEEK_MAIL_SUBJECT_PREFIX"] + subject,
        sender=current_app.config["LASTWEEK_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt.j2", **kwargs)
    msg.html = render_template(template + ".html.j2", **kwargs)
    mail.send(msg)