from os import path, environ

basedir = path.abspath(path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "dev secret key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(basedir, "data.sqlite")


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "testing secret key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ProductionConfig(Config):
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}