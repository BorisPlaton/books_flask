from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_uploads import configure_uploads, UploadSet, IMAGES

from bookreview.config import BaseConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'authorization.login'
login_manager.login_message = 'Войдите в аккаунт'
login_manager.login_message_category = 'warning'
bcrypt = Bcrypt()
mail = Mail()

profile = UploadSet("profile", IMAGES)
bookcover = UploadSet("bookcover", IMAGES)


def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    Migrate(app, db)
    from .models import User, Review, Comment

    configure_uploads(app, (profile, bookcover))

    from bookreview.utils import month_translate, delete_gaps
    app.jinja_env.globals['month_translate'] = month_translate
    app.jinja_env.globals['delete_gaps'] = delete_gaps

    from .views import authorization, main, settings, book
    app.register_blueprint(authorization)
    app.register_blueprint(main)
    app.register_blueprint(settings)
    app.register_blueprint(book)

    return app
