from flask_wtf import FlaskForm, Form
from wtforms.validators import InputRequired, EqualTo, Email
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, EmailField


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[InputRequired("Введите логин")])
    password = PasswordField("Пароль", validators=[InputRequired("Введите пароль")])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    login = StringField("Логин", validators=[InputRequired("Введите логин")])
    email = StringField("Почта", validators=[InputRequired("Введите почту"), Email("Введите почту")])
    password = PasswordField("Пароль", validators=[InputRequired("Введите пароль")])
    confirm_password = PasswordField("Повторите пароль", validators=[EqualTo('password', "Пароли должны совпадать")])
    submit = SubmitField("Зарегистрироваться")
