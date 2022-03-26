import os


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
