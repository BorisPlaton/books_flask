from flask import Blueprint, render_template, url_for, redirect, abort, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from bookreview.forms.forms import LoginForm, RegisterForm, RecoveryForm
from bookreview.models.models import User
from bookreview.func import send_reset_message, send_confirm_message
from bookreview import db, app

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


@routes.route("/recovery/<option>", methods=["POST", "GET"])
def recovery(option):
    """
    Восстановление пароля или логина.
    :param option:
        Параметр, который указывает, что нужно восстановить.
    """
    if option not in ("password", "login"):
        abort(404)

    recovery_form = RecoveryForm()
    form_title = "пароля" if option == "password" else "логина"

    if recovery_form.validate_on_submit():
        user = User.query.filter_by(email=recovery_form.email.data).first()

        send_reset_message(user, option)

        flash(f"На вашу почту было отправлено письмо для изменения {form_title}", category="success")
        return redirect(url_for('routes.login'))

    return render_template("recovery.html", form=recovery_form, title=form_title, option=option)


@routes.route("/confirm/<option>/<token>")
def confirm(token, option):
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt=option)
    user_id = s.loads(token, salt=option, max_age=1800)
    user = User.query.get(int(user_id))
    return f"{user}"


@routes.route("/confirm_registration/<token>")
def confirm_registration(token):

    if current_user.is_authenticated:  # Если пользователь авторизован возвращает на главную страницу
        return redirect(url_for('routes.index'))

    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    user_info = s.loads(token, max_age=1800)
    user = User(**user_info)
    db.session.add(user)
    db.session.commit()
    flash("Регистрация прошла успешно!", category="success")
    return redirect(url_for("routes.login"))


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
        send_confirm_message({
            "login": register_form.login.data,
            "email": register_form.email.data,
            "password": generate_password_hash(register_form.password.data).decode('utf-8'),
        })
        flash("На вашу почту было отправлено письмо для подтверждения регистрации", category="success")
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=register_form)


@routes.route('/logout')
@login_required
def logout():
    """
    Выход из учетной записи.
    """
    logout_user()
    return redirect(url_for('routes.login'))
