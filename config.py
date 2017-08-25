from os import environ


class BaseConfig:
    ARTICLE_COUNT_PER_PAGE = 10
    REVIEW_COUNT_PER_PAGE = 10

    # itsdangerous配置
    CONFIRM_TOKEN_SECRET_KEY = 'to generate a token hard to guess'

    SECRET_KEY = 'hello world'
    # flask-wtf配置
    CSRF_SECRET_KEY = "hello world"
    WTF_CSRF_SECRET_KEY = "secret key that no one can guess"

    # flask-sqlalchemy配置
    DATABASE_USERNAME = environ.get('DATABASE_USERNAME')
    DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@localhost/blog?charset=utf8mb4".\
                              format(DATABASE_USERNAME, DATABASE_PASSWORD)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_ECHO = False

    # 邮件配置
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

    BLOG_MAIL_SUBJECT_PREFIX = '[Blog]'
    BLOG_MAIL_SENDER = '[BLOG] ADMIN'

    ARTICLE_COUNT_PER_PAGE = 12
    HOT_TAG_COUNT = 9
    FAMOUS_USER_COUNT = 9

    @staticmethod
    def initApp(app):
        app.config.from_object(BaseConfig)


config = BaseConfig
