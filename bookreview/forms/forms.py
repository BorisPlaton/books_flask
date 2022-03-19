from flask_wtf import FlaskForm
from flask_bcrypt import check_password_hash
from wtforms.validators import InputRequired, EqualTo, Email, ValidationError
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField
from bookreview.models.models import User


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
    login = StringField("Логин", validators=[InputRequired("Введите логин")])
    email = StringField("Почта", validators=[InputRequired("Введите почту"), Email("Введите почту")])
    password = PasswordField("Пароль", validators=[InputRequired("Введите пароль")])
    confirm_password = PasswordField("Повторите пароль", validators=[EqualTo('password', "Пароли должны совпадать")])
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Такая почта уже зарегистрирована')

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Такой логин уже зарегистрирован')


class RecoveryForm(FlaskForm):
    email = StringField("Почта", validators=[InputRequired("Введите почту"), Email("Введите почту")])
    submit = SubmitField("Отправить")

    def validate_email(self, email):
        if not User.query.filter_by(email=email.data).first():
            raise ValidationError('Такой почты нет')
