from flask_login import UserMixin
from bookreview import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_photo = db.Column(db.Text, default='standard_user_pic.jpg')
    username = db.Column(db.String(24))
