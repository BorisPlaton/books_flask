from flask import Flask
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_uploads import configure_uploads, UploadSet, IMAGES
from flask_admin import Admin

from bookreview.config import BaseConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'authorization.login'
login_manager.login_message = 'Войдите в аккаунт'
login_manager.login_message_category = 'warning'
mail = Mail()
admin = Admin(name='Bookreview', template_mode='bootstrap4')

profile = UploadSet("profile", IMAGES)
bookcover = UploadSet("bookcover", IMAGES)


def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    from .models import User, Review, Comment
    Migrate(app, db)

    admin.add_view(ModelView(User, db.session, name='Пользователи'))
    admin.add_view(ModelView(Review, db.session, name='Рецензии'))
    admin.add_view(ModelView(Comment, db.session, name='Комментарии'))

    configure_uploads(app, (profile, bookcover))

    from bookreview.utils import month_translate
    app.jinja_env.globals['month_translate'] = month_translate

    from .views import authorization, main, settings, book, errors
    app.register_blueprint(authorization)
    app.register_blueprint(main)
    app.register_blueprint(settings)
    app.register_blueprint(book)
    app.register_blueprint(errors)

    return app
