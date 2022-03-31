from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash

from bookreview.forms import LoginForm, RegisterForm, EmailSendForm, SetNewPassword
from bookreview.models import User
from bookreview.utils import send_confirm_message, send_reset_message
from bookreview import db

authorization = Blueprint('authorization', __name__)


# @authorization.before_app_request
# def before_request():
#     if current_user.is_authenticated and not current_user.confirmed:
#         pass


@authorization.route('/login', methods=["POST", "GET"])
def login():
    """
    Страница авторизации.
    Корректность ввода данных, пароля и логина проверяется в bookreview.forms.forms.LoginForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(login=login_form.login.data).first()
        login_user(user, remember=login_form.remember)
        return redirect(url_for('main.index'))

    return render_template('login.html', form=login_form)


@authorization.route("/resset_password", methods=["POST", "GET"])
def resset_password():
    """
    Изменение пароля. Для восстановления пароля требуется ввести почту, на которую
    будет отправлено письмо.
    Корректность ввода данных и почты проверяется в bookreview.forms.forms.LoginForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    email_form = EmailSendForm()

    if email_form.validate_on_submit():
        user = User.query.filter_by(email=email_form.email.data).first()
        send_reset_message(user)
        flash(f"На вашу почту было отправлено письмо для изменения пароля", category="primary")
        return redirect(url_for('authorization.login'))

    return render_template("recovery.html", form=email_form)


@authorization.route("/set_new_password/<token>", methods=["POST", "GET"])
def set_new_password(token, user_id):
    """
    Изменение пароля пользователя со страницы входа в аккаунт.

    :param token: Токен URLSafeTimedSerializer c параметром
    :param user_id: ID пользователя
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    password_resset_form = SetNewPassword()
    user = User.query.get(int(user_id))

    if user and user.confirm_token(token):
        if password_resset_form.validate_on_submit():
            user.password = generate_password_hash(password_resset_form.new_password.data).encode('utf-8')
            db.session.commit()
            flash("Пароль успешно изменён", category="success")
            return redirect(url_for("authorization.login"))
    else:
        flash("Неверная ссылка")
    return render_template("set_new_password.html", form=password_resset_form, token=token)


@authorization.route("/confirm_registration/<token>")
@login_required
def confirm_registration(token):
    """
    Подтверждение регистрации пользователя

    :param token: токен URLSafeTimedSerializer
    """

    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if current_user.confirm_token(token):
        current_user.confirmed = True
        db.session.commit()
        flash("Вы подтвердили аккаунт", category="success")
    else:
        flash("Ссылка для подтверждения аккаунта недействительна", category="danger")

    return redirect(url_for('main.index'))


@authorization.route('/register', methods=["POST", "GET"])
def register():
    """
    Страница регистрации.
    Корректность ввода данных, пароля, уникальность логина и почты проверяется в bookreview.forms.forms.RegisterForm
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(login=register_form.login.data,
                    email=register_form.email.data,
                    password=generate_password_hash(register_form.password.data)
                    )
        db.session.add(user)
        db.session.commit()
        login_user(user)

        send_confirm_message(user)
        flash("На вашу почту отправлено письмо для подтверждения регистрации аккаунта", category="primary")
        return redirect(url_for("main.index"))

    return render_template('register.html', form=register_form)


@authorization.route('/logout')
@login_required
def logout():
    """
    Выход из учетной записи.
    """
    logout_user()
    flash("Вы вышли из аккаунта", category="primary")
    return redirect(url_for('authorization.login'))
