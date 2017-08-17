from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask import Flask
from config import config


db = SQLAlchemy()

loginManager = LoginManager()
loginManager.session_protection = "strong"
loginManager.login_view = "auth.login"

# 在所有视图中启用CSRF protect
csrfProtect = CSRFProtect()
mail = Mail()


def createApp():
    app = Flask(__name__)

    config.initApp(app)
    csrfProtect.init_app(app)
    loginManager.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    return app
