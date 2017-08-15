from os import environ


class BaseConfig:
    ARTICLE_COUNT_PER_PAGE = 10
    REVIEW_COUNT_PER_PAGE = 10
    CSRF_SECRET_KEY = "hello world"
    WTF_CSRF_SECRET_KEY = "secret key that no one can guess"
    DATABASE_USERNAME = environ.get('DATABASE_USERNAME')
    DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@localhost/blog".\
                              format(DATABASE_USERNAME, DATABASE_PASSWORD)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def initApp(app):
        app.config.from_object(BaseConfig)


config = BaseConfig
