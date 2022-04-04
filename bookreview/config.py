import os
from pathlib import Path


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("BOOKview", os.environ.get("MAIL_USERNAME"))
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    UPLOADED_PROFILE_DEST = 'bookreview/static/profile_img'
    UPLOADED_BOOKCOVER_DEST = 'bookreview/static/book_covers'

    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')


class DevConfig(BaseConfig):
    SQLALCHEMY_ECHO = False
    DEBUG = True


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.getcwd(), 'test.db')
    WTF_CSRF_ENABLED = False
    DEBUG = False
