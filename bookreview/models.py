import os
from datetime import datetime, date
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import Serializer, BadSignature, SignatureExpired
from sqlalchemy.orm.base import NO_VALUE
from werkzeug.security import generate_password_hash, check_password_hash

from bookreview import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


user_likes = db.Table('user_likes',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                      db.Column('review_id', db.Integer, db.ForeignKey('review.id', ondelete='CASCADE')))

user_dislikes = db.Table('user_dislikes',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                         db.Column('review_id', db.Integer, db.ForeignKey('review.id', ondelete='CASCADE')))

followers = db.Table('followers',
                     db.Column('follower', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                     db.Column('followed', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')))


class Permissions:
    """
    Привилегии пользователей.

    READ - чтение
    FOLLOW - следить за пользователями
    WRITE - писать комментарии, рецензии, добавлять книги
    DELETE - удалять комментарии, рецензии, книги
    MODERATE_COMS - удалять комментарии, рецензии других пользователей
    ADMINISTER - удалять пользователей, назначать роли, доступ к админке
    """
    READ = 1  # 0001
    FOLLOW = 2  # 0010
    WRITE = 4  # 0100
    DELETE = 8  # 1000
    MODERATE_COMS = 16  # 0001 0000
    LIKE = 32  # 0010 0000
    ADMINISTER = 128  # 1000 0000


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(32), unique=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def create_roles():
        roles_dict = {
            "UnconfirmedUser": Permissions.READ,
            "User": Permissions.READ | Permissions.FOLLOW | Permissions.WRITE | Permissions.DELETE | Permissions.LIKE,
            "Moderator": Permissions.READ | Permissions.FOLLOW | Permissions.WRITE | Permissions.DELETE |
                         Permissions.MODERATE_COMS | Permissions.LIKE,
            "Admin": Permissions.READ | Permissions.FOLLOW | Permissions.WRITE | Permissions.DELETE |
                     Permissions.MODERATE_COMS | Permissions.ADMINISTER | Permissions.LIKE,
        }
        for (role, permission) in roles_dict.items():
            # Проверяем присутствие новых ролей
            if not Role.query.filter_by(role=role).first():
                new_role = Role(role=role, permissions=permission)
                db.session.add(new_role)
            # Проверяем не изменились ли разрешения старых ролей
            elif Role.query.filter_by(role=role).first().permissions != permission:
                old_role = Role.query.filter_by(role=role).first()
                old_role.permissions = permission
        db.session.commit()

    def __repr__(self):
        return f"{self.role} | {self.permissions} "


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(200), nullable=False)
    profile_photo = db.Column(db.String(200), default='default_user_img.jpg')
    username = db.Column(db.String(24))

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    reviews = db.relationship("Review", backref="author", passive_deletes=True, lazy='dynamic')
    likes = db.relationship("Review", backref="users_like", secondary=user_likes, passive_deletes=True)
    dislikes = db.relationship("Review", backref="users_dislike", secondary=user_dislikes, passive_deletes=True)
    comments = db.relationship("Comment", backref="author")
    books = db.relationship("Book", backref="user", passive_deletes=True, lazy='dynamic')
    # На кого подписан
    followed = db.relationship("User", backref=db.backref('followers', lazy='dynamic'),
                               secondary=followers, lazy='dynamic',
                               primaryjoin=(followers.c.follower == id), secondaryjoin=(followers.c.followed == id))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = self.login
        if not self.role:
            self.role = Role.query.filter_by(role='UnconfirmedUser' if not self.confirmed else "User").first()

    def can(self, permission):
        return self.role.permissions & permission == permission

    def is_admin(self):
        return self.can(Permissions.ADMINISTER)

    @staticmethod
    def create_password_hash(target, value, oldvalue, initiator):
        """
        Автоматически хэширует пароль
        """
        if oldvalue is not NO_VALUE and check_password_hash(oldvalue, value):
            return oldvalue
        return generate_password_hash(value)

    @staticmethod
    def set_confirmed_account(target, value, oldvalue, initiator):
        """
        Устанавливает роль пользователя на "User" после подтверждения регистрации
        """
        target.role = Role.query.filter_by(role='User').first()

    @staticmethod
    def create_fake(count=10):
        """
        Случайно созданные пользователи для тестовых данных.
        Может получиться меньше пользователей чем в параметре count,
        если будет вызываться ошибка IntegrityError.

        :param count: Количество новых пользователей
        """
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        for i in range(count):
            u = User(
                login=forgery_py.internet.user_name(),
                email=forgery_py.internet.email_address(),
                confirmed=True,
                password="1",
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def popularity(self):
        return sum([review.popularity for review in self.reviews])

    @property
    def reviews_amount(self):
        return len(list(self.reviews))

    @property
    def books_amount(self):
        return len(list(self.books))

    @property
    def follow_amount(self):
        return len(self.followed.all())

    @property
    def followers_amount(self):
        return len(self.followers.all())

    def is_following(self, user_id):
        return self.followed.filter(followers.c.followed == user_id).first()

    def follow(self, user_id):
        if not self.is_following(user_id):
            user = User.query.get(user_id)
            self.followed.append(user)

    def unfollow(self, user_id):
        if self.is_following(user_id):
            user = User.query.get(user_id)
            self.followed.remove(user)

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


db.event.listen(User.password, 'set', User.create_password_hash, retval=True)
db.event.listen(User.confirmed, 'set', User.set_confirmed_account)


class AnonymousUser(AnonymousUserMixin):

    def can(self, permission):
        return False

    def is_admin(self):
        return False

    @property
    def confirmed(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    popularity = db.Column(db.Integer, nullable=False, default=0)
    text = db.Column(db.String(8000), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    comments = db.relationship("Comment", backref="review", passive_deletes=True, lazy='dynamic')

    @staticmethod
    def create_fake(count=25):
        """
        Случайно созданные рецензии для тестовых данных.
        Может получиться меньше пользователей чем в параметре count,
        если будет вызываться ошибка IntegrityError.

        :param count: Количество новых записей
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
    text = db.Column(db.String(600), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"id comment {self.id} | Text {self.text}"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(200), default="default_cover_img.jpg")
    description = db.Column(db.String(350))

    # Пользователь, который создал эту книгу
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    review = db.relationship('Review', backref='book', passive_deletes=True)

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
