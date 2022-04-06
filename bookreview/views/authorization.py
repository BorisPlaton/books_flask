from flask_mail import Message

from flask import Blueprint, render_template, url_for, redirect, flash
from flask_login import current_user, login_user, logout_user, login_required

from bookreview.forms import LoginForm, RegisterForm, EmailSendForm, SetNewPassword
from bookreview.models import User
from bookreview import db, mail

authorization = Blueprint('authorization', __name__)


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
        user_id = User.query.filter_by(email=email_form.email.data).first().id
        return redirect(url_for('authorization.send_reset_message', user_id=user_id))

    return render_template("recovery.html", form=email_form)


@authorization.route("/send_reset_message/<int:user_id>", methods=["POST", "GET"])
def send_reset_message(user_id):
    """
    Отправляет лист на почту пользователя со ссылкой для изменения пароля.

    :param user_id: Id Пользователя, которому отправляется письмо
    """
    user = User.query.get_or_404(user_id)
    msg = Message(f'Изменение пароля', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб изменить пароль, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.set_new_password', token=user.generate_token(), _external=True)}"""
    mail.send(msg)
    flash(f"На вашу почту было отправлено письмо для изменения пароля", category="primary")
    return redirect(url_for('authorization.login'))


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
            user.password = password_resset_form.new_password.data
            db.session.commit()
            flash("Пароль успешно изменён", category="success")
            return redirect(url_for("authorization.login"))
    else:
        flash("Неверная ссылка")
    return render_template("set_new_password.html", form=password_resset_form, token=token)


@authorization.route("/confirm_account")
@login_required
def confirm_account():
    if not current_user.confirmed:
        return render_template('confirm_account.html')
    flash('Вы уже подтвердили свой аккаунт', category='primary')
    return redirect(url_for('main.index'))


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


@authorization.route('/send_confirm_message')
def send_confirm_message():
    """
    Отправляет письмо с подтверждением регистрации
    """
    if not current_user.confirmed:
        msg = Message(f'Подтверждение регистрации', recipients=[current_user.email])
        msg.body = f"""Перейдите по ссылке, чтоб подтвердить регистрацию, если вы этого не делали, тогда просто проигнорируйте это письмо:
    {url_for('authorization.confirm_registration', token=current_user.generate_token(), user_id=current_user.id, _external=True)}"""
        mail.send(msg)
        flash("На вашу почту отправлено письмо для подтверждения регистрации аккаунта", category="primary")
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
                    password=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('authorization.send_confirm_message'))

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
