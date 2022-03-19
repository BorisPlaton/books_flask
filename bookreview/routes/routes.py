from flask import Blueprint, render_template, url_for, redirect, abort
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import check_password_hash, generate_password_hash
from bookreview.forms.forms import LoginForm, RegisterForm, RecoveryForm
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
        login_user(user)
        return "Вы вошли"

    return render_template('login.html', form=login_form)


@routes.route("/recovery/<option>")
def recovery(option: str):
    """
    Восстановление пароля или логина.
    :param option: Путь, который указывает, что нужно восстановить
    """
    recovery_form = RecoveryForm()
    if option in ("password", "login"):
        form_title = "пароля" if option == "password" else "логина"
        return render_template("recovery.html", form=recovery_form, title=form_title)
    abort(404)


@routes.route('/register', methods=["POST", "GET"])
def register():
    """
    Страница регистрации.
    Уникальность логина и почты проверяется в модуле forms.
    """

    if current_user.is_authenticated:  # Если пользователь авторизован возвращает на главную страницу
        return redirect(url_for('routes.index'))

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(
            login=register_form.login.data,
            email=register_form.email.data,
            password=generate_password_hash(register_form.password.data, ).decode('utf-8'),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('routes.index'))

    return render_template('register.html', form=register_form)


@routes.route('/logout')
@login_required
def logout():
    """
    Выход из учетной записи.
    """
    logout_user()
    return redirect(url_for('routes.login'))
