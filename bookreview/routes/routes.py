from flask import Blueprint, render_template, url_for, redirect, abort, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_bcrypt import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bookreview.forms.forms import LoginForm, RegisterForm, EmailSendForm, SetNewPassword
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
    Корректность ввода данных, пароля и логина проверяется в bookreview.forms.forms.LoginForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(login=login_form.login.data).first()
        login_user(user)
        return "Вы вошли"

    return render_template('login.html', form=login_form)


@routes.route("/resset_password", methods=["POST", "GET"])
def resset_password():
    """
    Восстановление пароля.
    Корректность ввода данных и почты проверяется в bookreview.forms.forms.LoginForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    email_form = EmailSendForm()

    if email_form.validate_on_submit():
        user = User.query.filter_by(email=email_form.email.data).first()

        send_reset_message(user)

        flash(f"На вашу почту было отправлено письмо для изменения пароля", category="primary")
        return redirect(url_for('routes.login'))

    return render_template("recovery.html", form=email_form)


@routes.route("/set_new_password/<token>", methods=["POST", "GET"])
def set_new_password(token):
    """
    Изменение пароля пользователя со страницы входа в аккаунт.

    :param token: Токен URLSafeTimedSerializer c параметром
    """

    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    password_resset_form = SetNewPassword()

    try:
        user_id = s.loads(token, max_age=1800)["id"]
        if password_resset_form.validate_on_submit():
            user = User.query.get(int(user_id))
            user.password = generate_password_hash(password_resset_form.new_password.data)
            db.session.commit()
            flash("Пароль успешно изменён", category="success")
            return redirect(url_for("routes.login"))
        return render_template("set_new_password.html", form=password_resset_form, token=token)
    except BadSignature:
        flash("Неверная ссылка", category='danger')
    except SignatureExpired:
        flash("Срок действия ссылки истёк", category='danger')

    return redirect(url_for('routes.login'))


@routes.route("/confirm_registration/<token>")
def confirm_registration(token):
    """
    Подтверждение регистрации пользователя и занесения его в базу данных.

    :param token: токен URLSafeTimedSerializer
    """

    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        user_info = s.loads(token, max_age=1800)
        user = User(**user_info)
        db.session.add(user)
        db.session.commit()
        flash("Регистрация прошла успешно!", category="success")
    except BadSignature:
        flash("Неверная ссылка", category='danger')
    except SignatureExpired:
        flash("Срок действий ссылки истёк", category="danger")

    return redirect(url_for("routes.login"))


@routes.route('/register', methods=["POST", "GET"])
def register():
    """
    Страница регистрации.
    Корректность ввода данных, пароля, уникальность логина и почты проверяется в bookreview.forms.forms.RegisterForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        send_confirm_message({
            "login": register_form.login.data,
            "email": register_form.email.data,
            "password": generate_password_hash(register_form.password.data).decode('utf-8'),
        })
        flash("На вашу почту было отправлено письмо для подтверждения регистрации", category="primary")
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
