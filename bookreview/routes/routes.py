from flask import Blueprint, render_template, url_for, redirect, flash
from flask_login import current_user, login_user
from flask_bcrypt import check_password_hash, generate_password_hash
from bookreview.forms.forms import LoginForm, RegisterForm
from bookreview.models.models import User
from bookreview import db

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    """
    Домашняя страница.
    """
    return render_template('index.html')


@routes.route('/login', methods=["POST", "GET"])
def login():
    """
    Страница авторизации.
    """

    if current_user.is_authenticated:  # Если пользователь авторизован возвращает на главную страницу
        return redirect(url_for('routes.index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(login=login_form.login.data).first()
        if user and check_password_hash(user.password, login_form.password.data):  # Проверяем корректность данных
            login_user(user)
            return "Вы вошли"
        flash("Неправильный логин или пароль", category="danger")

    return render_template('login.html', form=login_form)


@routes.route('/register', methods=["POST", "GET"])
def register():
    """
    Страница регистрации.
    """

    if current_user.is_authenticated:  # Если пользователь авторизован возвращает на главную страницу
        return redirect(url_for('routes.index'))

    register_form = RegisterForm()
    if register_form.validate_on_submit():

        if User.query.filter_by(login=register_form.login.data).all():
            flash("Пользователь с таким логином уже есть", category="danger")
        elif User.query.filter_by(email=register_form.email.data).all():
            flash("Пользователь с такой почтой уже есть", category="danger")
        else:
            user = User(
                login=register_form.login.data,
                email=register_form.email.data,
                password=generate_password_hash(register_form.password.data, ).decode('utf-8'),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('routes.index'))
        return redirect(url_for('routes.register'))

    return render_template('register.html', form=register_form)
