from flask import render_template
from flask_mail import Message
from . import mail
from appInstance import app


def sendMail(reciever, subject, contentTemplate, **kwargs):
    message = Message(app['BLOG_MAIL_SUBJECT_PREFIX'] + subject,
                      sender=app.config['BLOG_MAIL_SENDER'],
                      recipients=[reciever])
    message.html = render_template(contentTemplate, **kwargs)
    mail.send(message)
