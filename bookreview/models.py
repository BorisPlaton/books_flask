from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager


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
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_photo = db.Column(db.String(200), default='default_user_img.jpg')
    username = db.Column(db.String(24), default=same_as('login'))
    reviews = db.relationship("Review", backref="author")
    comments = db.relationship("Comment", backref="author")
    books = db.relationship("Book", backref="user")

    def __repr__(self):
        return f"id user {self.id} | Login {self.login} | Email {self.email} | password {self.password}"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    text = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    good_marks = db.Column(db.Integer, default=0)
    bad_marks = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", backref="review")

    def __repr__(self):
        return f"id review {self.id} | Title {self.title}"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"id comment {self.id} | Text {self.text} | Author {self.author}"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Пользователь, который создал эту книгу
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(200), default="default_cover_img.jpg")
    description = db.Column(db.String(350))
    review = db.relationship('Review', backref='book', uselist=False)

    def __repr__(self):
        return f"id book {self.id} | title {self.title} | Author {self.author}"
