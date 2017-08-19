from flask import render_template, current_app
from flask_mail import Message, Mail


mail = Mail()


def sendMail(reciever, subject, contentTemplate, **kwargs):
    message = Message(current_app['BLOG_MAIL_SUBJECT_PREFIX'] + subject,
                      sender=current_app.config['BLOG_MAIL_SENDER'],
                      recipients=[reciever])
    message.html = render_template(contentTemplate, **kwargs)
    mail.send(message)
