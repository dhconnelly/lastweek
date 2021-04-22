from os import path, environ

basedir = path.abspath(path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
    LASTWEEK_MAIL_SUBJECT_PREFIX = "[lastweek] "
    LASTWEEK_MAIL_SENDER = "lastweek admin <admin@lastweek.dev>"
    LASTWEEK_ADMIN = environ.get("LASTWEEK_ADMIN")
    LASTWEEK_SNIPPETS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEV = True
    DEBUG = True
    SECRET_KEY = "dev secret key"
    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + path.join(basedir, "data.sqlite")


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "testing secret key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "lastweek-test.localdomain"


class ProductionConfig(Config):
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}