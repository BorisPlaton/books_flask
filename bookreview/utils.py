from flask import url_for
from flask_mail import Message

from bookreview import mail


def send_reset_message(user):
    """
    Отправляет лист на почту пользователя со ссылкой для изменения пароля.

    :param user: Пользователь, которому отправляется письмо
    """
    msg = Message(f'Изменение пароля', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб изменить пароль, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.set_new_password', token=user.generate_token(), _external=True)}"""
    mail.send(msg)


def send_confirm_message(user):
    """
    Отправляет письмо с подтверждением регистрации

    :param user: Пользователь
    """
    msg = Message(f'Подтверждение регистрации', recipients=[user.email])
    msg.body = f"""Перейдите по ссылке, чтоб зарегистрироваться, если вы этого не делали, тогда просто проигнорируйте это письмо:
{url_for('authorization.confirm_registration', token=user.generate_token(), user_id=user.id, _external=True)}"""
    mail.send(msg)

