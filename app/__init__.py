from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import config


db = SQLAlchemy()

loginManager = LoginManager()
loginManager.session_protection = "strong"
loginManager.login_view = "auth.login"

# 在所有视图中启用CSRF protect
csrfProtect = CSRFProtect()


def createApp():
    app = Flask(__name__)

    config.initApp(app)
    csrfProtect.init_app(app)
    loginManager.init_app(app)
    db.init_app(app)

    return app
