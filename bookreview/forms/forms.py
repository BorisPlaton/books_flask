from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from flask_bcrypt import check_password_hash
from wtforms.validators import InputRequired, EqualTo, Email, ValidationError, Length, Regexp
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField
from bookreview.models import User
from bookreview import profile_img


class LoginForm(FlaskForm):
    """
    Форма для авторизации пользователя при входе на сайт.
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
    Форма для регистрации пользователя.
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
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Такая почта уже зарегистрирована')

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Такой логин уже зарегистрирован')


class EmailSendForm(FlaskForm):
    """
    Форма для отправки письма пользователю.
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
    Форма для изменения пароля
    """
    new_password = PasswordField("Пароль", validators=[InputRequired("Введите новый пароль")])
    confirm_new_password = PasswordField("Повторите пароль",
                                         validators=[EqualTo('new_password', message="Пароли должны совпадать")])
    submit = SubmitField("Сохранить")


class ChangeUsername(FlaskForm):
    """
    Форма для изменения имя пользователя
    """
    username = StringField("Имя пользователя", validators=[InputRequired("Введите новое имя")])
    submit = SubmitField("Сохранить")


class LoadPhoto(FlaskForm):
    photo = FileField("Загрузить фото", validators=[FileRequired("Загрузите фото"),
                                                    FileSize(max_size=1000000,
                                                             message="Файл должен весить меньше 1 Мб"),
                                                    FileAllowed(profile_img, 'Только фото')])
    submit = SubmitField("Сохранить")


class DeletePhoto(FlaskForm):
    submit = SubmitField("Удалить фото")
