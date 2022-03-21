from flask_login import UserMixin
from bookreview import db, login_manager


def same_as(column):
    """
    Устанавливает значение default равным другой колонке в таблице SQLAlchemy
    :param column: название колонки
    """
    def func(context):
        return context.get_current_parameters()[column]
    return func


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_photo = db.Column(db.Text, default='standard_user_pic.jpg')
    username = db.Column(db.String(24), default=same_as('login'))

    def __repr__(self):
        return f"User {self.id} | {self.login} | {self.email}"
