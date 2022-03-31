import os
from datetime import datetime, date

from flask_login import UserMixin
from itsdangerous import Serializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

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


user_likes = db.Table('user_likes',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                      db.Column('review_id', db.Integer, db.ForeignKey('review.id', ondelete='CASCADE')))

user_dislikes = db.Table('user_dislikes',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                         db.Column('review_id', db.Integer, db.ForeignKey('review.id', ondelete='CASCADE')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(200), nullable=False)
    profile_photo = db.Column(db.String(200), default='default_user_img.jpg')
    username = db.Column(db.String(24), default=same_as('login'))

    reviews = db.relationship("Review", backref="author", passive_deletes=True, lazy='dynamic')
    likes = db.relationship("Review", backref="users_like", secondary=user_likes, passive_deletes=True)
    dislikes = db.relationship("Review", backref="users_dislike", secondary=user_dislikes, passive_deletes=True)
    comments = db.relationship("Comment", backref="author")
    books = db.relationship("Book", backref="user", passive_deletes=True, lazy='dynamic')

    @staticmethod
    def create_fake(count=10):
        """
        Случайно созданные пользователи для тестовых данных.
        Может получиться меньше пользователей чем в параметре count,
        если будет вызываться ошибка IntegrityError.

        :param count: Количество новых пользователей
        :return:
        """
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        for i in range(count):
            u = User(
                login=forgery_py.internet.user_name(),
                email=forgery_py.internet.email_address(),
                confirmed=True,
                password=generate_password_hash("1")
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def popularity(self):
        return sum([review.popularity for review in self.reviews])

    def confirm_token(self, token, expiration=3600):
        s = Serializer(os.environ.get('SECRET_KEY'))
        try:
            user_id = s.loads(token, max_age=expiration)
            if user_id.get("id") == self.id:
                return self.id
        except (BadSignature, SignatureExpired):
            return False

    def generate_token(self):
        s = Serializer(os.environ.get('SECRET_KEY'))
        return s.dumps({"id": self.id})

    def __repr__(self):
        return f"id user {self.id} | Login {self.login} | Email {self.email} | password {self.password}"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    popularity = db.Column(db.Integer, nullable=False, default=0)
    text = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    comments = db.relationship("Comment", backref="review", passive_deletes=True, lazy='dynamic')

    @staticmethod
    def create_fake(count=25):
        """
        Случайно созданные рецензии для тестовых данных.
        Может получиться меньше пользователей чем в параметре count,
        если будет вызываться ошибка IntegrityError.

        :param count: Количество новых записей
        :return:
        """
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py

        users = User.query.filter(User.id == Book.user_id).all()

        for i in range(count):
            user_id = random.choice(users).id
            r = Review(
                author_id=user_id,
                book_id=random.choice(Book.query.filter_by(user_id=user_id).all()).id,
                text=forgery_py.lorem_ipsum.sentences()
            )
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"id review {self.id} | {self.text}"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete='CASCADE'), nullable=False)

    text = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"id comment {self.id} | Text {self.text}"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Пользователь, который создал эту книгу
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(200), default="default_cover_img.jpg")
    description = db.Column(db.String(350))

    review = db.relationship('Review', backref='book', passive_deletes=True, lazy=True)

    @staticmethod
    def create_fake(count=25):
        """
        Случайно созданные книги для тестовых данных.
        Может получиться меньше книг чем в параметре count,
        если будет вызываться ошибка IntegrityError.

        :param count: Количество новых книг
        """
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py

        users = User.query.all()

        for i in range(count):
            b = Book(
                user_id=random.choice(users).id,
                title=forgery_py.lorem_ipsum.title(),
                author=forgery_py.name.full_name(),
                description=forgery_py.lorem_ipsum.sentence()
            )
            db.session.add(b)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"{self.author} - {self.title}"
