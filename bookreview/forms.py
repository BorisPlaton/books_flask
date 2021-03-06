from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from flask_login import current_user
from werkzeug.security import check_password_hash
from wtforms.validators import InputRequired, EqualTo, Email, ValidationError, Length, Regexp
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from bookreview.models import User, Book
from bookreview import profile


class LoginForm(FlaskForm):
    """
    Авторизация пользователя при входе на сайт.
    Проверяет правильность ввода пароля и логина. В ином случае вызывает ошибку ValidationError.
    """
    login = StringField("Логин", validators=[InputRequired("Введите логин")])
    password = PasswordField("Пароль", validators=[InputRequired("Введите пароль")])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")

    def validate_login(self, login):
        if not User.query.filter_by(login=login.data).first():
            raise ValidationError('Неверный логин')

    def validate_password(self, password):
        user = User.query.filter_by(login=self.login.data).first()
        if user and not check_password_hash(user.password, password.data):
            raise ValidationError('Неверный пароль')


class RegisterForm(FlaskForm):
    """
    Регистрация пользователя.
    Проверяет уникальность логина и почты. В ином случае вызывает ошибку ValidationError.
    """
    login = StringField("Логин", validators=[InputRequired("Введите логин"),
                                             Length(max=24),
                                             Regexp("^[A-Za-z1-9._]*$",
                                                    message="Логин может содержать только буквы латиницы, цифры, точку и нижнее подчеркивание")
                                             ])
    email = StringField("Почта", validators=[InputRequired("Введите почту"), Email("Введите почту")])
    password = PasswordField("Пароль", validators=[InputRequired("Введите пароль"),
                                                   Regexp("^[A-Za-z1-9]*$",
                                                          message="Пароль может содержать только цифры и буквы латиницы")
                                                   ])
    confirm_password = PasswordField("Повторите пароль", validators=[EqualTo('password', "Пароли должны совпадать")])
    recaptcha = RecaptchaField()
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Такая почта уже зарегистрирована')

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Такой логин уже зарегистрирован')


class EmailSendForm(FlaskForm):
    """
    Отправка письма пользователю при регистрации.
    Проверяет правильность существование почты. В ином случае вызывает ошибку ValidationError.
    """
    email = StringField("Почта", validators=[InputRequired("Введите почту"), Email("Введите почту")])
    submit = SubmitField("Отправить")

    def validate_email(self, email):
        """
        Проверяет существование почты только если данные в поле email корректны.
        """
        if not self.email.errors and not User.query.filter_by(email=email.data).first():
            raise ValidationError('Такой почты нет')


class SetNewPassword(FlaskForm):
    """
    Изменение пароля пользователя
    """
    new_password = PasswordField("Новый пароль", validators=[InputRequired("Введите новый пароль")])
    confirm_new_password = PasswordField("Повторите пароль",
                                         validators=[EqualTo('new_password', message="Пароли должны совпадать")])
    submit = SubmitField("Сохранить")


class ChangePassword(SetNewPassword):
    """
    Изменение пароля пользователя со странички настройки
    """
    old_password = PasswordField("Старый пароль", validators=[InputRequired("Введите старый пароль")])

    def validate_old_password(self, old_password):
        if not self.old_password.errors and not check_password_hash(current_user.password, old_password.data):
            raise ValidationError("Неверный пароль")


class ChangeUsername(FlaskForm):
    """
    Изменения имя пользователя
    """
    username = StringField("Имя пользователя", validators=[InputRequired("Введите новое имя"), Length(max=24),
                                                           Regexp(regex="^(?:[\w]+\s?)+$",
                                                                  message="Неверный ввод имени")])
    submit = SubmitField("Сохранить")


class LoadPhoto(FlaskForm):
    """
    Загрузка фото пользователя
    """
    photo = FileField("Загрузить фото", validators=[FileRequired("Загрузите фото"),
                                                    FileSize(max_size=1000000,
                                                             message="Файл должен весить меньше 1 Мб"),
                                                    FileAllowed(profile, 'Только фото')])
    submit = SubmitField("Сохранить")


class Delete(FlaskForm):
    """
    Удаление фото пользователя
    """
    submit = SubmitField("Удалить")


class DeleteAccount(FlaskForm):
    old_password = PasswordField("Старый пароль", validators=[InputRequired("Введите старый пароль")])
    submit = SubmitField("Удалить аккаунт")

    def validate_old_password(self, old_password):
        if not check_password_hash(current_user.password, old_password.data):
            raise ValidationError("Неверный пароль")


def _choice_query():
    """
    Возвращает пользователю список книг
    """
    return Book.query.filter_by(user_id=current_user.id)


class WriteReview(FlaskForm):
    """
    Написание рецензии на книгу
    """
    select_book = QuerySelectField("Книга", query_factory=_choice_query,
                                   validators=[InputRequired("Выберите книгу")])
    text = TextAreaField("Отзыв", validators=[InputRequired("Это поле не может быть пустым"),
                                              Length(max=10000)])
    submit = SubmitField("Сохранить")


class AddBook(FlaskForm):
    title = StringField("Название", validators=[InputRequired("Введите название книги"),
                                                Length(max=200)])
    author = StringField("Автор", validators=[InputRequired("Введите автора"),
                                              Length(max=100)])
    cover = FileField("Обложка", validators=[FileSize(max_size=2000000,
                                                      message="Обложка должна весить не больше 2 Мб")])
    description = TextAreaField("Описание книги", validators=[Length(max=350)])
    submit = SubmitField("Сохранить")


class WriteComment(FlaskForm):
    text = TextAreaField("Комментарий", validators=[InputRequired("Это поле не может быть пустым"),
                                                    Length(max=1000)])
    submit = SubmitField("Оставить комментарий")


class SearchQuery(FlaskForm):
    text = StringField("Введите запрос")
    submit = SubmitField("Поиск")
