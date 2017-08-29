from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from config import config
from .models import db, AnonymousUser, User
from .email import mail
from .auth import auth
from .main import main
from .user import user

loginManager = LoginManager()
loginManager.session_protection = "strong"
loginManager.login_view = "auth.login"
loginManager.anonymous_user = AnonymousUser


@loginManager.user_loader
def loadUser(userId):
    return User.query.filter_by(id=userId).first()


# 在所有视图中启用CSRF protect
csrfProtect = CSRFProtect()


def createApp():
    app = Flask(__name__)

    config.initApp(app)
    csrfProtect.init_app(app)
    loginManager.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(user, url_prefix='/user')

    return app
